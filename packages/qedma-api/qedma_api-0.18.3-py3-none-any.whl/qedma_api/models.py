"""Qedma Public API"""

# pylint: disable=missing-function-docstring,missing-class-docstring,missing-module-docstring
import contextlib
import datetime
import enum
import re
from collections.abc import Generator
from typing import Annotated, Literal, TypeAlias

import loguru
import pydantic
import qiskit.qasm3
import qiskit.quantum_info
from typing_extensions import NotRequired, Self, TypedDict

from qedma_api import pauli_utils


logger = loguru.logger


class RequestBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=False,
    )


class ResponseBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="ignore",
        validate_assignment=True,
        arbitrary_types_allowed=False,
    )


class JobStatus(str, enum.Enum):
    """The status of a job."""

    ESTIMATING = "ESTIMATING"
    """Job was created and QESEM is currently estimating it."""
    ESTIMATED = "ESTIMATED"
    """Job was estimated. Issue the `qedma_client.start_job()` api request to initiate the execution."""  # pylint: disable=line-too-long
    RUNNING = "RUNNING"
    """Job started running. Monitor its progress using the `qedma_client.wait_for_job_complete()`
    method."""
    SUCCEEDED = "SUCCEEDED"
    """Job finished successfully. The user can now get the results via the `qedma_client.get_job()`
    API with the include_results = True flag."""
    FAILED = "FAILED"
    "Job failed. Review the error message in the `job.errors` field." ""
    CANCELLED = "CANCELLED"
    "The job was cancelled by the user."

    def __str__(self) -> str:
        return self.value


class TranspilationLevel(enum.IntEnum):
    LEVEL_0 = 0
    """
    Minimal transpilation: the mitigated circuit will closely resemble the input
    circuit structurally.
    """
    LEVEL_1 = 1
    """ Prepares several alternative transpilations and chooses the one that minimizes QPU time."""


class IBMQProvider(RequestBase):
    name: Literal["ibmq"] = "ibmq"
    token_ref: str | None = None
    instance: str
    channel: Literal["ibm_quantum_platform", "ibm_cloud"] = "ibm_quantum_platform"


def _unique_qubit_indices(value: str) -> str:
    """
    Ensure that every qubit index is referenced at most once.
    The Pauli string syntax is restricted by ``_PAULI_STRING_REGEX_STR`` to
    be a comma-separated list of terms such as ``"X_0"`` or ``"r_15"``.
    Extract the trailing integer of each term and verify uniqueness.
    """
    if value == "I":
        return value

    ops_groups_pattern = re.compile(_TERM_GROUP_REGEX)
    ops_groups = sorted(
        ((op_match, q_match) for op_match, q_match in ops_groups_pattern.findall(value)),
        key=lambda x: x[1],
    )
    all_qubits = [q for _, q in ops_groups]

    if not len(set(all_qubits)) == len(all_qubits):
        raise ValueError(
            f"Observable term contains multiple operations for the same qubit: {value}"
        )

    return ",".join("".join(g) for g in ops_groups)


_TERM_GROUP_REGEX = r"([XYZ01rl+\-])_*(\d+)"
_TERM_STRING_REGEX = rf"^{_TERM_GROUP_REGEX}(,{_TERM_GROUP_REGEX})*$"
_TERM_STRING_OR_I_REGEX = rf"({_TERM_STRING_REGEX})|(^I$)"

ObsTerm = Annotated[
    str,
    pydantic.Field(pattern=_TERM_STRING_OR_I_REGEX),
    pydantic.AfterValidator(_unique_qubit_indices),
    pydantic.BeforeValidator(lambda s: s.replace("_", "")),
]


class ObservableMetadata(pydantic.BaseModel):
    """Metadata for a quantum observable."""

    description: str
    "Description of the observable"


def _term_to_repr(term: ObsTerm) -> ObsTerm:
    term = term.replace("_", "")
    return ",".join(f"{q_term[0]}_{q_term[1:]}" for q_term in term.split(","))


class Observable(pydantic.RootModel[dict[ObsTerm, float]]):
    """A quantum observable represented as a mapping of ObsTerm strings to their coefficients."""

    @pydantic.model_validator(mode="after")
    def validate_not_all_terms_are_i(self) -> Self:
        if all(p == "I" for p in self):
            raise ValueError("At least one Term must be non-identity")
        return self

    def __iter__(self) -> Generator[ObsTerm, None, None]:  # type: ignore[override]
        # pydantic suggests to override __iter__ method (
        # https://docs.pydantic.dev/latest/concepts/models/#rootmodel-and-custom-root-types)
        # but __iter__ method is already implemented in pydantic.BaseModel, so we just ignore the
        # warning and hope that it works as expected (tests covers dump/load methods and iter)
        yield from iter(self.root)

    def __getitem__(self, key: ObsTerm) -> float:
        return self.root[pydantic.TypeAdapter(ObsTerm).validate_python(key)]

    def __contains__(self, key: ObsTerm) -> bool:
        return pydantic.TypeAdapter(ObsTerm).validate_python(key) in self.root

    def __len__(self) -> int:
        return len(self.root)

    def __str__(self) -> str:
        return str(self.root)

    def __repr__(self) -> str:
        return (
            "Observable({"
            + ", ".join(f"'{_term_to_repr(t)}': {c}" for t, c in self.root.items())
            + "})"
        )

    def __hash__(self) -> int:
        return hash(tuple(self.root.items()))

    @property
    def qubits(self) -> set[int]:
        """
        Returns a set of qubits that are used in the observable.
        """
        qubit_idx_pattern = re.compile(_TERM_GROUP_REGEX)
        return set().union(
            *((int(q) for _, q in qubit_idx_pattern.findall(s)) for s in self.root if s != "I")
        )

    @staticmethod
    def observables_to_qubits(observables: list["Observable"]) -> set[int]:
        """
        Returns a set of qubits that are used in the observables.
        """
        return set().union(*(o.qubits for o in observables))

    @classmethod
    def from_sparse_pauli_op(  # type: ignore[no-any-unimported]
        cls, pauli_op: qiskit.quantum_info.SparsePauliOp
    ) -> "Observable":
        """Convert a qiskit.quantum_info.SparsePauliOp to an Observable.

        SparsePauliOp, like all of qiskit, uses little-endian convention.
        This means that the operator Pauli("XY") or SparsePauliOp(["XY"],[1])
        have the "X" acting on qubit 1 and "Y" acting on qubit 0.

        :param pauli_op: The SparsePauliOp to convert
        :return: An Observable instance representing the same operator
        :raises ValueError: If the SparsePauliOp contains phases or complex coefficients,
            or if it contains only identity Paulis with zero coefficients
        """
        if any(p.phase != 0 for p in pauli_op.paulis):
            raise ValueError("The `PauliList` of the `SparsePauliOp` must not contain phases")

        if any(c.imag != 0 for c in pauli_op.coeffs):
            raise ValueError("The `coeffs` of the `SparsePauliOp` must be real")

        pauli_op = pauli_op.simplify()

        observable_dict = {
            pauli_utils.qiskit_pauli_to_pauli(p.to_label()): float(c.real)
            for p, c in zip(pauli_op.paulis, pauli_op.coeffs, strict=True)
        }

        return cls(root=observable_dict)

    def to_sparse_pauli_op(  # type: ignore[no-any-unimported]
        self, num_qubits: int | None = None
    ) -> qiskit.quantum_info.SparsePauliOp:
        """
        Convert this Observable to a qiskit.quantum_info.SparsePauliOp.

        SparsePauliOp, like all of qiskit, uses little-endian convention.
        This means that the operator Pauli("XY") or SparsePauliOp(["XY"],[1])
        have the "X" acting on qubit 1 and "Y" acting on qubit 0.

        :param num_qubits: The number of qubits in the resulting SparsePauliOp. If None,
         it will be determined from the highest qubit index in the observable
        """
        if len(self.root) == 0:
            return qiskit.quantum_info.SparsePauliOp(["I"], [0.0])

        if num_qubits is None:
            num_qubits = max(self.qubits, default=0) + 1

        paulis, coeffs = zip(*self.root.items())
        return qiskit.quantum_info.SparsePauliOp(
            [pauli_utils.pauli_to_qiskit_pauli(p, num_qubits) for p in paulis], coeffs
        )

    @classmethod
    def from_sparse_observable(  # type: ignore[no-any-unimported]
        cls, sparse_obs: qiskit.quantum_info.SparseObservable
    ) -> "Observable":
        """
        Convert a qiskit.quantum_info.SparseObservable to an Observable.

        SparseObservable, like all of qiskit, uses little-endian convention.
        This means that the operator SparseObservable("XY")
        have the "X" acting on qubit 1 and "Y" acting on qubit 0.

        :param sparse_obs: The qiskit.quantum_info.SparseObservable to convert
        :return: An Observable instance representing the same operator
        :raises ValueError: If the SparseObservable contains phases or complex coefficients,
            or if it contains only identity Paulis with zero coefficients
        """
        if any(c.imag != 0 for c in sparse_obs.coeffs):
            raise ValueError("The `coeffs` of the `SparsePauliOp` must be real")

        sparse_obs = sparse_obs.simplify()

        def _build_term_string(  # type: ignore[no-any-unimported]
            ops: tuple[qiskit.quantum_info.SparseObservable.BitTerm, ...],
            qubits: tuple[int, ...],
        ) -> ObsTerm:
            if len(ops) == len(qubits) == 0:
                return "I"
            return ",".join(f"{q_op}{q}" for q_op, q in zip(ops, qubits, strict=True))

        observable_dict = {
            _build_term_string(ops, qs): float(c.real)
            for (ops, qs, c) in sparse_obs.to_sparse_list()
        }

        return cls(root=observable_dict)

    def to_sparse_observable(  # type: ignore[no-any-unimported]
        self, num_qubits: int | None = None
    ) -> qiskit.quantum_info.SparseObservable:
        """
        Convert this Observable to a qiskit.quantum_info.SparseObservable.

        SparseObservable, like all of qiskit, uses little-endian convention.
        This means that the operator SparseObservable("XY")
        have the "X" acting on qubit 1 and "Y" acting on qubit 0.

        :param num_qubits: The number of qubits in the resulting SparseObservable. If None,
         it will be determined from the highest qubit index in the observable
        """

        if num_qubits is None:
            num_qubits = max(self.qubits, default=0) + 1

        if len(self.root) == 0:
            return qiskit.quantum_info.SparseObservable.from_terms([], num_qubits)

        return qiskit.quantum_info.SparseObservable.from_terms(
            [
                qiskit.quantum_info.SparseObservable.Term(
                    num_qubits, c, *_term_string_to_qiskit_term(t)
                )
                for t, c in self.root.items()
            ],
            num_qubits,
        )


def _term_string_to_qiskit_term(  # type: ignore[no-any-unimported]
    term: ObsTerm,
) -> tuple[tuple[qiskit.quantum_info.SparseObservable.BitTerm, ...], tuple[int, ...]]:
    if term == "I":
        return (), ()

    ops_groups_pattern = re.compile(_TERM_GROUP_REGEX)
    ops_groups = [
        (qiskit.quantum_info.SparseObservable.BitTerm[q_op], int(q))
        for q_op, q in ops_groups_pattern.findall(term)
    ]
    return tuple(zip(*ops_groups))  # type: ignore[return-value]


SparseObservable: TypeAlias = Observable


class ExpectationValue(ResponseBase):
    """Result of a quantum measurement, containing both the measured value and its uncertainty."""

    value: float
    "The expected value of the quantum measurement"

    error_bar: float
    "The standard error associated with the measurement"

    def __str__(self) -> str:
        return f"{self.value} ± {self.error_bar}"


class ExpectationValues(pydantic.RootModel[list[tuple[Observable, ExpectationValue]]]):
    """Collection of quantum measurement results, pairing observables with their
    measured expectation values."""

    def __iter__(self) -> Generator[tuple[Observable, ExpectationValue], None, None]:  # type: ignore[override] # pylint: disable=line-too-long
        # pydantic suggests to override __iter__ method (
        # https://docs.pydantic.dev/latest/concepts/models/#rootmodel-and-custom-root-types)
        # but __iter__ method is already implemented in pydantic.BaseModel, so we just ignore the
        # warning and hope that it works as expected (tests covers dump/load methods and iter)
        yield from iter(self.root)

    def __getitem__(self, key: int) -> tuple[Observable, ExpectationValue]:
        return self.root[key]

    def __len__(self) -> int:
        return len(self.root)

    def __str__(self) -> str:
        return "[" + ", ".join([f"{obs}: ({exp})" for obs, exp in self.root]) + "]"

    def __repr__(self) -> str:
        return (
            "ExpectationValues(["
            + ",".join([f"{repr(obs)}: {repr(exp)}" for obs, exp in self.root])
            + "])"
        )


class QiskitExpectationValues(list[tuple[qiskit.quantum_info.SparseObservable, ExpectationValue]]):  # type: ignore[no-any-unimported] # pylint: disable=line-too-long
    """
    Collection of quantum measurement results, pairing Qiskit ExpectationValue objects with their
    measured expectation values.
    """

    def __str__(self) -> str:
        return "[" + ", ".join([f"{obs}: ({exp})" for obs, exp in self]) + "]"

    def __repr__(self) -> str:
        parts = [f"{repr(obs)}: {repr(exp)}" for obs, exp in self]
        return f"QiskitExpectationValues([{','.join(parts)}])"

    @classmethod
    def from_expectation_values(
        cls, expectation_values: ExpectationValues
    ) -> "QiskitExpectationValues":
        return cls([(obs.to_sparse_observable(), exp) for obs, exp in expectation_values.root])


class PrecisionMode(str, enum.Enum):
    """
    Precision mode types when executing a parameterized circuit.
    """

    JOB = "JOB"
    """ QESEM will treat the `precision` as a precision for the sum of the expectation values."""
    CIRCUIT = "CIRCUIT"
    """ QESEM will target the specified `precision` for each circuit."""

    def __str__(self) -> str:
        return self.value


class ExecutionMode(str, enum.Enum):
    """The mode of execution."""

    SESSION = "SESSION"
    """ QESEM will execute the job in a single IBM dedicated session."""
    BATCH = "BATCH"
    """ QESEM will execute the job in multiple IBM batches."""

    def __str__(self) -> str:
        return self.value


class JobOptions(RequestBase):
    """Additional options for a job request"""

    execution_mode: ExecutionMode = pydantic.Field(default=ExecutionMode.BATCH)
    """ Execution mode type. Default is BATCH"""


class CircuitOptions(RequestBase):
    """Qesem circuits circuit_options"""

    error_suppression_only: bool = False
    """ No error mitigation. This results in a much shorter but biased run. When True, the `shots`
    parameter becomes mandatory, while precision and observables will be ignored!"""

    transpilation_level: TranspilationLevel = pydantic.Field(default=TranspilationLevel.LEVEL_1)
    """ Transpilation level type"""

    parallel_execution: bool = False
    """
    Whether to parallel the circuit over multiple copies (if possible).
    Useful for small circuits over large QPUs.
    """


def _check_circuit(  # type: ignore[no-any-unimported]
    value: qiskit.QuantumCircuit | str,
) -> qiskit.QuantumCircuit:
    if isinstance(value, str):
        with contextlib.suppress(Exception):
            value = qiskit.qasm3.loads(value)

    if isinstance(value, str):
        with contextlib.suppress(Exception):
            value = qiskit.QuantumCircuit.from_qasm_str(value)

    if not isinstance(value, qiskit.QuantumCircuit):
        raise ValueError("Circuit must be a valid Qiskit QuantumCircuit or QASM string")

    return value


def _serialize_circuit(value: qiskit.QuantumCircuit) -> str:  # type: ignore[no-any-unimported]
    result = qiskit.qasm3.dumps(value)
    if not isinstance(result, str):
        raise ValueError("Failed to serialize the circuit")

    return result


class ParameterizedCircuit(RequestBase):  # type: ignore[no-any-unimported]
    circuit: qiskit.QuantumCircuit  # type: ignore[no-any-unimported]
    "The quantum circuit to be executed."

    parameters: dict[str, tuple[float, ...]] | None = None
    "Optional dictionary mapping parameter names to their values for parameterized circuits. "

    @pydantic.field_validator("circuit", mode="plain", json_schema_input_type=str)
    @classmethod
    def check_circuit(cls, value: qiskit.QuantumCircuit | str) -> qiskit.QuantumCircuit:  # type: ignore[no-any-unimported] # pylint: disable=line-too-long
        return _check_circuit(value)

    @pydantic.field_serializer("circuit", mode="plain", return_type=str)
    def serialize_circuit(self, value: qiskit.QuantumCircuit) -> str:  # type: ignore[no-any-unimported] # pylint: disable=line-too-long
        return _serialize_circuit(value)

    @pydantic.model_validator(mode="after")
    def check_parameters(self) -> "ParameterizedCircuit":
        if self.parameters is None:
            if len(set(map(str, self.circuit.parameters))) > 0:
                raise ValueError("Parameters must match the circuit parameters")
            return self

        if set(map(str, self.parameters.keys())) != set(map(str, self.circuit.parameters)):
            raise ValueError("Parameters must match the circuit parameters")

        if len(self.parameters) > 0:
            if any(
                re.search(r"[^\w\d]", p, flags=re.U)
                for p in self.parameters  # pylint: disable=not-an-iterable
            ):
                raise ValueError(
                    "Parameter names must contain only alphanumeric characters, got: "
                    f"{list(self.parameters.keys())}"
                )

            # check all parameters are of the same length
            parameter_value_lengths = set(len(v) for v in self.parameters.values())
            if len(parameter_value_lengths) > 1:
                raise ValueError("All parameter values must have the same length")

        return self


class Circuit(ParameterizedCircuit):  # type: ignore[no-any-unimported]
    """A quantum circuit configuration including the circuit itself,
    observables to measure, and execution parameters."""

    observables: tuple[Observable, ...]
    """Tuple of observables to be measured. Each observable represents a measurement
    configuration."""

    observables_metadata: tuple[ObservableMetadata, ...] | None = None
    """Tuple of metadata for the observables.
    Each metadata corresponds to the observable at the same index."""

    precision: float
    "Target precision for the expectation value measurements"

    options: CircuitOptions
    "Additional options for circuit execution"

    @pydantic.model_validator(mode="after")
    def check_parameters_and_observables(self) -> "Circuit":
        if self.parameters and len(self.parameters) > 0:
            # check that the number of observables is equal to the number of parameters values
            parameter_value_lengths = set(len(v) for v in self.parameters.values())
            if len(self.observables) != list(parameter_value_lengths)[0]:
                raise ValueError(
                    "Number of observables must be equal to the number of parameter values"
                )

        if self.observables_metadata is not None and len(self.observables_metadata) != len(
            self.observables
        ):
            raise ValueError(
                "The number of observable metadata items must match the number of observables"
            )

        return self

    @pydantic.field_validator("options")
    @classmethod
    def validate_error_suppression_only(cls, value: CircuitOptions) -> CircuitOptions:
        if value.error_suppression_only:
            raise ValueError("Wrong circuit type!")
        return value


class ErrorSuppressionCircuit(ParameterizedCircuit):  # type: ignore[no-any-unimported]
    shots: int
    """Amount of shots to run this circuit. Only viable when error-suppression only is True!"""

    options: CircuitOptions
    "Additional options for circuit execution"

    @pydantic.field_validator("options")
    @classmethod
    def validate_error_suppression_only(cls, value: CircuitOptions) -> CircuitOptions:
        if not value.error_suppression_only:
            raise ValueError("Wrong circuit type!")
        return value


class QPUTime(TypedDict):
    """Time metrics for quantum processing unit (QPU) usage."""

    execution: datetime.timedelta
    "Actual time spent executing the quantum circuit on the QPU"

    estimation: NotRequired[datetime.timedelta]
    "Estimated time required for QPU execution, may not be present"


class TranspiledCircuit(pydantic.BaseModel):  # type: ignore[no-any-unimported]
    """Circuit to be executed on QPU"""

    circuit: qiskit.QuantumCircuit  # type: ignore[no-any-unimported]
    """The quantum circuit after optimization, ready for execution."""

    qubit_maps: list[dict[int, int]] = pydantic.Field(
        validation_alias=pydantic.AliasChoices("qubit_maps", "qubit_map")
    )
    """
    A list of mapping between logical qubits in the original circuit and physical qubits on the
    QPU, one for each copy of the original circuit (if parallel execution is not used, will
    contain only one mapping).
    """

    num_measurement_bases: int
    "Number of different measurement bases required for this circuit"

    @pydantic.field_validator("qubit_maps", mode="before")
    @classmethod
    def qubit_map_backward_compatibility(
        cls, value: list[dict[int, int]] | dict[int, int]
    ) -> list[dict[int, int]]:
        # qubit map was a dict in the past
        if isinstance(value, dict):
            return [value]

        return value

    @pydantic.field_validator("circuit", mode="plain", json_schema_input_type=str)
    @classmethod
    def check_circuit(  # type: ignore[no-any-unimported]
        cls,
        value: qiskit.QuantumCircuit | str,
    ) -> qiskit.QuantumCircuit:
        return _check_circuit(value)

    @pydantic.field_serializer("circuit", mode="plain", return_type=str)
    def serialize_circuit(  # type: ignore[no-any-unimported]
        self,
        value: qiskit.QuantumCircuit,
    ) -> str:
        return _serialize_circuit(value)


class ExecutionDetails(ResponseBase):
    """Detailed statistics about the quantum circuit execution."""

    total_shots: int
    "Total number of times the quantum circuit was executed"

    mitigation_shots: int
    "Number of shots used for error mitigation"

    gate_fidelities: dict[str, float]
    "Dictionary mapping gate names to their measured fidelities on the QPU"

    transpiled_circuits: list[TranspiledCircuit] | None = None
    """List of circuits after optimization and mapping to the QPU architecture."""


class JobStep(pydantic.BaseModel):
    """Represents a single step in a job progress"""

    name: Annotated[str, pydantic.Field(description="The name of the step")]


class JobProgress(pydantic.BaseModel):
    """Represents job progress, i.e. a list of sequential steps"""

    steps: Annotated[
        list[JobStep],
        pydantic.Field(
            description="List of steps corresponding to JobStep values",
            default_factory=list,
        ),
    ]


class JobDetails(ResponseBase):
    """Detailed information about a quantum job, including its status, execution details,
    and results."""

    account_id: str
    "The unique identifier of the user account"

    account_email: str
    "The email address associated with the user account"

    job_id: str
    "The unique identifier of the job"

    description: str = ""
    "Optional description of the job"

    masked_account_token: str
    "Partially hidden account authentication token"

    masked_qpu_token: str
    "Partially hidden QPU access token"

    qpu_name: str
    "Name of the quantum processing unit (or simulator) being used"

    circuit: Circuit | ErrorSuppressionCircuit | None = None
    "The quantum circuit to be executed. Returns only if `include_circuit` is True"

    precision_mode: PrecisionMode | None = None
    "The precision mode used for execution. Can only be used when parameters are set."

    status: JobStatus
    "Current status of the job"

    analytical_qpu_time_estimation: datetime.timedelta | None
    "Theoretical estimation of QPU execution time"

    empirical_qpu_time_estimation: datetime.timedelta | None = None
    "Measured estimation of QPU execution time based on actual runs"

    total_execution_time: datetime.timedelta
    "Total time taken for the job execution. Includes QPU and classical processing time."

    created_at: datetime.datetime
    "Timestamp when the job was created"

    updated_at: datetime.datetime
    "Timestamp when the job was last updated"

    qpu_time: QPUTime | None
    "Actual QPU time used for execution and estimation."

    qpu_time_limit: datetime.timedelta | None = None
    "Maximum allowed QPU execution time"

    warnings: list[str] | None = None
    "List of warning messages generated during job execution"

    errors: list[str] | None = None
    "List of error messages generated during job execution"

    intermediate_results: ExpectationValues | None = None
    "Partial results obtained during job execution."

    results: ExpectationValues | list[dict[int, int]] | None = None
    "Final results of the quantum computation. Returns only if `include_results` is True"

    noisy_results: ExpectationValues | list[dict[int, int]] | None = None
    "Results without error mitigation applied."

    execution_details: ExecutionDetails | None = None
    "Information about the execution process. Includes total shots, mitigation shots, and gate fidelities."  # pylint: disable=line-too-long

    progress: JobProgress | None = None
    "Current progress information of the job. Printed automatically when calling `qedma_client.wait_for_job_complete()`."  # pylint: disable=line-too-long

    execution_mode: ExecutionMode
    "The mode of execution."

    enable_notifications: bool = True
    "Whether to enable email notifications for this job."

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)
