# pylint: disable=too-many-lines
"""Qedma Public API"""

import datetime
import importlib.metadata
import json
import math
import os
import sys
import threading
import time
from collections.abc import Mapping, Sequence
from typing import TypeAlias, overload

import loguru
import pydantic
import qiskit
import qiskit.quantum_info
import requests
from typing_extensions import Self

from qedma_api import models


STATUS_POLLING_INTERVAL = datetime.timedelta(seconds=10)
PROGRESS_POLLING_INTERVAL = datetime.timedelta(seconds=10)

ObservablesGroups: TypeAlias = (  # type: ignore[no-any-unimported]
    models.Observable
    | qiskit.quantum_info.SparseObservable
    | qiskit.quantum_info.SparsePauliOp
    | Sequence[
        models.Observable | qiskit.quantum_info.SparsePauliOp | qiskit.quantum_info.SparseObservable
    ]
)


class JobRequest(models.RequestBase):
    """Request to create a new job"""

    circuit: models.Circuit | models.ErrorSuppressionCircuit
    provider: models.IBMQProvider
    backend: str
    empirical_time_estimation: bool
    precision_mode: models.PrecisionMode | None = None
    description: str = ""
    enable_notifications: bool = True

    @pydantic.model_validator(mode="after")
    def validate_precision_mode(self) -> Self:
        """Validates the precision mode."""
        if isinstance(self.circuit, models.ErrorSuppressionCircuit):
            return self

        if (self.circuit.parameters is None) != (self.precision_mode is None):
            raise ValueError("Parameters and precision mode must be both set or unset")
        return self


class StartJobRequest(models.RequestBase):
    """Start a job."""

    max_qpu_time: datetime.timedelta
    options: models.JobOptions
    force_start: bool = False


class GetJobsDetailsResponse(models.ResponseBase):
    """An internal object."""

    jobs: list[models.JobDetails]


class RegisterQpuTokenRequest(models.RequestBase):
    """Store qpu token request model"""

    qpu_token: str


class DecomposeResponse(models.ResponseBase):
    """Decompose response model"""

    parametrized_circ: str
    meas_params: dict[str, list[float]]
    obs_per_basis: list[models.Observable]
    relative_l2_trunc_err: float


class QedmaServerError(Exception):
    """An exception raised when the server returns an error."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details is None:
            return super().__str__()
        return f"{super().__str__()}. Details: {self.details}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message}, details={self.details})"


class ResultNotReadyError(QedmaServerError):
    """An exception raised when the server returns an error."""

    def __init__(self) -> None:
        super().__init__("Result is not ready yet")


class ClientJobDetails(pydantic.BaseModel):
    """Detailed information about a quantum job, including its status, execution details,
    and results.
    Same as JobDetails, but meant to be returned to the client."""

    model_config = pydantic.ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

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

    circuit: models.Circuit | models.ErrorSuppressionCircuit | None = None
    "The quantum circuit to be executed. Returns only if `include_circuit` is True"

    precision_mode: models.PrecisionMode | None = None
    "The precision mode used for execution. Can only be used when parameters are set."

    status: models.JobStatus
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

    qpu_time: models.QPUTime | None
    "Actual QPU time used for execution and estimation."

    qpu_time_limit: datetime.timedelta | None = None
    "Maximum allowed QPU execution time"

    warnings: list[str] | None = None
    "List of warning messages generated during job execution"

    errors: list[str] | None = None
    "List of error messages generated during job execution"

    intermediate_results: models.ExpectationValues | None = None
    "Partial results obtained during job execution."

    results: (
        models.QiskitExpectationValues | models.ExpectationValues | list[dict[int, int]] | None
    ) = None
    "Final results of the quantum computation. Returns only if `include_results` is True"

    noisy_results: (
        models.QiskitExpectationValues | models.ExpectationValues | list[dict[int, int]] | None
    ) = None
    "Results without error mitigation applied."

    execution_details: models.ExecutionDetails | None = None
    "Information about the execution process. Includes total shots, mitigation shots, and gate fidelities."  # pylint: disable=line-too-long

    progress: models.JobProgress | None = None
    "Current progress information of the job. Printed automatically when calling `qedma_client.wait_for_job_complete()`."  # pylint: disable=line-too-long

    execution_mode: models.ExecutionMode
    "The mode of execution."

    enable_notifications: bool = True
    "Whether to enable email notifications for this job."

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    @classmethod
    def from_job_details(
        cls, job_details: models.JobDetails, qedma_observable_model: bool = False
    ) -> "ClientJobDetails":
        """
        Convert a JobDetails object to a ClientJobDetails object.
        :param job_details: The JobDetails object to convert.
        :param qedma_observable_model: Whether to return the results with Qedma's observable model,
         or Qiskit SparsePauliOp.
        :return: The converted ClientJobDetails object.
        """
        job = cls(**job_details.model_dump())

        if qedma_observable_model:
            return job
        if job_details.results is not None and isinstance(
            job_details.results, models.ExpectationValues
        ):
            job.results = models.QiskitExpectationValues.from_expectation_values(
                job_details.results
            )

        if job_details.noisy_results is not None and isinstance(
            job_details.noisy_results, models.ExpectationValues
        ):
            job.noisy_results = models.QiskitExpectationValues.from_expectation_values(
                job_details.noisy_results
            )
        return job


ENDPOINT_URI = "https://api.qedma.io/v2/qesem"


class Client:  # pylint: disable=missing-class-docstring
    def __init__(
        self,
        *,
        api_token: str | None = None,
        provider: models.IBMQProvider | None = None,
        uri: str = ENDPOINT_URI,
        timeout: int = 60,
    ) -> None:
        self.api_token = api_token
        self.provider = provider
        self.uri = uri
        self.timeout = timeout
        self._logger_scope = "qedma-api/client"
        self.logger = loguru.logger.bind(scope=self._logger_scope)
        self._headers = {
            "Authorization": f"Bearer {self.api_token}",
            "X-Qedma-Client-Version": importlib.metadata.version("qedma_api"),
        }
        self._config_loguru()

    def set_provider(self, provider: models.IBMQProvider) -> None:
        """Set the provider of the client. (e.g. IBMQProvider)"""
        self.provider = provider

    @overload  # QESEM without parameters
    def create_job(  # type: ignore[no-any-unimported]  # pylint: disable=too-many-arguments
        self,
        *,
        circuit: qiskit.QuantumCircuit,
        observables: ObservablesGroups,
        observables_metadata: Sequence[models.ObservableMetadata] | None = None,
        parameters: None = None,
        precision: float,
        backend: str,
        empirical_time_estimation: bool = False,
        description: str = "",
        circuit_options: models.CircuitOptions | None = None,
        precision_mode: None = None,
    ) -> ClientJobDetails: ...

    @overload  # QESEM with parameters
    def create_job(  # type: ignore[no-any-unimported]  # pylint: disable=too-many-arguments
        self,
        *,
        circuit: qiskit.QuantumCircuit,
        observables: ObservablesGroups,
        observables_metadata: Sequence[models.ObservableMetadata] | None = None,
        parameters: Mapping[str | qiskit.circuit.Parameter, Sequence[float]],
        precision: float,
        backend: str,
        empirical_time_estimation: bool = False,
        description: str = "",
        circuit_options: models.CircuitOptions | None = None,
        precision_mode: models.PrecisionMode,
    ) -> ClientJobDetails: ...

    @overload  # QES
    def create_job(  # type: ignore[no-any-unimported]  # pylint: disable=too-many-arguments
        self,
        *,
        circuit: qiskit.QuantumCircuit,
        shots: int,
        parameters: Mapping[str | qiskit.circuit.Parameter, Sequence[float]] | None = None,
        backend: str,
        description: str = "",
        circuit_options: models.CircuitOptions | None = None,
    ) -> ClientJobDetails: ...

    def create_job(  # type: ignore[no-any-unimported]  # pylint: disable=too-many-arguments,too-many-branches,too-many-locals
        self,
        *,
        circuit: qiskit.QuantumCircuit,
        observables: ObservablesGroups | None = None,
        observables_metadata: Sequence[models.ObservableMetadata] | None = None,
        parameters: Mapping[str | qiskit.circuit.Parameter, Sequence[float]] | None = None,
        precision: float | None = None,
        backend: str,
        empirical_time_estimation: bool = False,
        description: str = "",
        circuit_options: models.CircuitOptions | None = None,
        precision_mode: models.PrecisionMode | None = None,
        shots: int | None = None,
        enable_notifications: bool = True,
    ) -> ClientJobDetails:
        """
        Submit a new job to the API Gateway.
        :param circuit: The circuit to run.
        :param observables: The observables to measure.
         Can be either models.Observable, Sequence[models.Observable],
         or qiskit.quantum_info.SparsePauliOp.
        :param precision: The target absolute precision to achieve for each input observable.
        :param backend: The backend (QPU) to run on. (e.g., `ibm_fez`)
        :param parameters: Used when a parameterized circuit is provided. The parameters to run the
         circuit with (mapping from parameter to sequence of values, all parameters must have the
         same number of values) If given, the number of observables must be equal to the number
         of values.
        :param empirical_time_estimation: Whether to use empirical time estimation.
        :param description: A description for the job.
        :param circuit_options: Additional options for a circuit.
        :param precision_mode: The precision mode to use. Can only be used when parameters are set.
        :param shots: The number of shots to execute. Only used when error_suppression_only=True.
        :param enable_notifications: Whether to enable email notifications for this job.
        :return: The job's details including its ID.
        """

        if circuit_options is None:
            circuit_options = models.CircuitOptions()

        if self.provider is None:
            raise ValueError("Provider is not set")

        if observables is not None:

            if isinstance(
                observables,
                (
                    models.Observable,
                    qiskit.quantum_info.SparsePauliOp,
                    qiskit.quantum_info.SparseObservable,
                ),
            ):
                observables = (observables,)

            new_observables = []
            for obs in observables:

                if isinstance(obs, qiskit.quantum_info.SparsePauliOp):
                    obs = models.Observable.from_sparse_pauli_op(obs)

                if isinstance(obs, qiskit.quantum_info.SparseObservable):
                    obs = models.Observable.from_sparse_observable(obs)

                new_observables.append(obs)

            observables = tuple(new_observables)

        if observables_metadata is not None:
            if observables is None or len(observables_metadata) != len(observables):
                raise ValueError(
                    "Observables metadata provided but did not match the number of observables"
                )

        circ: models.Circuit | models.ErrorSuppressionCircuit
        if not circuit_options.error_suppression_only:
            if not observables:
                raise ValueError("Observables are mandatory!")
            if not precision:
                raise ValueError("Precision is mandatory!")
            if shots:
                raise ValueError("Shots are not supported when error_suppression_only is disabled")

            circ = models.Circuit(
                circuit=circuit,
                parameters=(
                    {str(k): tuple(v) for k, v in parameters.items()}
                    if parameters is not None
                    else None
                ),
                observables=tuple(observables),
                observables_metadata=(
                    tuple(observables_metadata) if observables_metadata is not None else None
                ),
                precision=precision,
                options=circuit_options,
            )
        else:
            if observables:
                raise ValueError(
                    "Observables are not supported when error_suppression_only is enabled"
                )
            if precision:
                raise ValueError(
                    "Precision is not supported when error_suppression_only is enabled"
                )
            if empirical_time_estimation:
                raise ValueError(
                    "Time estimation is not supported when error_suppression_only is enabled"
                )
            if not shots:
                raise ValueError("shots is mandatory when error_suppression_only is enabled")

            circ = models.ErrorSuppressionCircuit(
                circuit=circuit,
                shots=shots,
                parameters=(
                    {str(k): tuple(v) for k, v in parameters.items()}
                    if parameters is not None
                    else None
                ),
                options=circuit_options,
            )

        self.logger.info("Submitting new job")
        response = requests.post(
            url=f"{self.uri}/job",
            data=JobRequest(
                circuit=circ,
                provider=self.provider,
                empirical_time_estimation=empirical_time_estimation,
                backend=backend,
                description=description,
                precision_mode=precision_mode,
                enable_notifications=enable_notifications,
            ).model_dump_json(),
            headers=self._headers,
            timeout=self.timeout,
        )

        self._raise_for_status(response)

        resp = models.JobDetails.model_validate_json(response.content)
        client_job_details = ClientJobDetails.from_job_details(resp)

        self.logger.info("[{job_id}] New job created", job_id=resp.job_id)

        self._print_warnings_and_errors(client_job_details)

        return client_job_details

    def start_job(
        self,
        job_id: str,
        max_qpu_time: datetime.timedelta,
        options: models.JobOptions | None = None,
        force_start: bool = False,
    ) -> None:
        """
        Start running an estimation job.
        :param job_id: The ID of the job.
        :param max_qpu_time: The maximum allowed QPU time.
        :param options: Additional options for the job (see `JobOptions`).
        :param force_start: If True, the job will automatically start once the estimation completes.
        """
        if options is None:
            options = models.JobOptions()

        job = self._get_jobs([job_id])[0]
        if (not force_start) and job.status == models.JobStatus.ESTIMATING:
            self.logger.error(
                "[{job_id}] It is not allowed to issue start_job until it is in status ESTIMATED. Please wait for the estimation to complete.",  # pylint: disable=line-too-long
                job_id=job_id,
            )
            return
        if job.status not in {
            models.JobStatus.ESTIMATING,
            models.JobStatus.ESTIMATED,
        }:
            self.logger.error(
                "[{job_id}] It is not allowed to issue start_job after the job has started or completed. ",  # pylint: disable=line-too-long
                job_id=job_id,
            )
            return

        self.logger.info("[{job_id}] Starting job", job_id=job_id)

        response = requests.post(
            url=f"{self.uri}/job/{job_id}/start",
            data=StartJobRequest(
                max_qpu_time=max_qpu_time, options=options, force_start=force_start
            ).model_dump_json(),
            headers=self._headers,
            timeout=self.timeout,
        )

        self._raise_for_status(response)

    def _create_decompose_task(
        self,
        mpo_file: str,
        *,
        max_bases: int,
        l2_truncation_err: float,
        op_l2_norm: float,
        k: int,
        pauli_coeff_th: float,
    ) -> str:
        self.logger.info("Requesting decomposition of MPO")
        if not os.path.exists(mpo_file):
            raise FileNotFoundError(f"File {mpo_file} not found")
        if not os.path.isfile(mpo_file):
            raise FileNotFoundError(f"File {mpo_file} is not a file")

        with open(mpo_file, "rb") as data_file:
            response = requests.post(
                url=f"{self.uri}/hpc/decompose",
                params=[
                    ("max_bases", max_bases),
                    ("l2_truncation_err", l2_truncation_err),
                    ("op_l2_norm", op_l2_norm),
                    ("k", k),
                    ("pauli_coeff_th", pauli_coeff_th),
                ],
                files={"data_file": data_file},
                headers=self._headers,
                timeout=datetime.timedelta(minutes=5).total_seconds(),
            )

        if response.status_code == 404:
            raise QedmaServerError("API endpoint not enabled")

        self._raise_for_status(response)

        resp_json = response.json()
        if "task_id" not in resp_json:
            raise QedmaServerError("Task ID not found in response", details=resp_json)

        task_id = resp_json["task_id"]
        if not isinstance(task_id, str):
            raise QedmaServerError("Invalid task ID in response", details=resp_json)

        return task_id

    def _get_decompose_task_result(
        self, task_id: str, *, max_retries: int = 5
    ) -> DecomposeResponse:
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url=f"{self.uri}/hpc/decompose/{task_id}",
                    headers=self._headers,
                    timeout=60 * 10,
                )
            except requests.Timeout:
                if attempt == max_retries - 1:
                    self.logger.error(
                        "[{task_id}] Timeout while waiting for decomposition task result. ",
                        task_id=task_id,
                    )
                    raise
                self.logger.error(
                    "[{task_id}] Timeout while waiting for decomposition task result. "
                    "Retrying...",
                    task_id=task_id,
                )
                time.sleep(0.3)
                continue

            if response.status_code == 200:
                return DecomposeResponse.model_validate_json(response.content)

            if response.status_code == 202:
                raise ResultNotReadyError()

            self.logger.error(
                "[{task_id}] Failed to get decomposition task result ({status_code}). "
                "Retrying...",
                task_id=task_id,
                status_code=response.status_code,
            )
            time.sleep(0.3)

        if response is not None:
            self._raise_for_status(response)
        raise QedmaServerError("Failed to get decomposition task result after max retries")

    def decompose(  # type: ignore[no-any-unimported]  # pylint: disable=missing-function-docstring
        self,
        mpo_file: str,
        *,
        max_bases: int,
        l2_truncation_err: float = 1e-12,
        observable: models.Observable | qiskit.quantum_info.SparsePauliOp,
        k: int = 1000,
        pauli_coeff_th: float = 1e-8,
        timeout: datetime.timedelta = datetime.timedelta(minutes=60),
    ) -> DecomposeResponse:
        if isinstance(observable, qiskit.quantum_info.SparsePauliOp):
            observable = models.Observable.from_sparse_pauli_op(observable)

        op_l2_norm = math.sqrt(sum(coeff**2 for p, coeff in observable.root.items()))

        task_id = self._create_decompose_task(
            mpo_file,
            max_bases=max_bases,
            l2_truncation_err=l2_truncation_err,
            op_l2_norm=op_l2_norm,
            k=k,
            pauli_coeff_th=pauli_coeff_th,
        )
        self.logger.info("Decomposition task created. task_id: [{task_id}]", task_id=task_id)

        start = datetime.datetime.now()
        while datetime.datetime.now() - start < timeout:
            time.sleep(0.5)
            try:
                return self._get_decompose_task_result(task_id)
            except ResultNotReadyError:
                pass

        raise TimeoutError("Decomposition task timed out")

    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a job. Please note that the `cancel_job` API will prevent QESEM from sending
        new circuits to the QPU. Circuits which are already running on the QPU cannot be cancelled.

        :param job_id: The job_id to cancel
        """
        self.logger.info("[{job_id}] Canceling job", job_id=job_id)
        response = requests.post(
            url=f"{self.uri}/job/{job_id}/cancel",
            headers=self._headers,
            timeout=self.timeout,
        )

        self._raise_for_status(response)

    def get_job(
        self,
        job_id: str,
        *,
        include_circuits: bool = False,
        include_results: bool = False,
        qedma_observable_model: bool = False,
    ) -> ClientJobDetails:
        """
        Get a job's details.
        :param job_id: The ID of the job.
        :param include_circuits: Whether to include the input circuit.
        :param include_results: Whether to include the result of the job (if it is ready).
        :param qedma_observable_model: Whether to return the results with Qedma's observable model,
         or Qiskit SparsePauliOp.
        :return: Details about the job, with the data from the flags.
        """
        client_job_details = self.get_jobs(
            [job_id],
            include_circuits=include_circuits,
            include_results=include_results,
            qedma_observable_model=qedma_observable_model,
        )[0]

        self._print_warnings_and_errors(client_job_details)

        return client_job_details

    def get_jobs(
        self,
        jobs_ids: list[str],
        *,
        include_circuits: bool = False,
        include_results: bool = False,
        qedma_observable_model: bool = False,
    ) -> list[ClientJobDetails]:
        """
        Get multiple jobs' details.
        :param jobs_ids: The IDs of the jobs.
        :param include_circuits: Whether to include the input circuits.
        :param include_results: Whether to include the results of the jobs (if they are ready).
        :param qedma_observable_model: Whether to return the results with Qedma's observable model,
         or Qiskit SparsePauliOp.
        :return: Details about the jobs, with the data from the flags.
        """
        self.logger.info("Querying jobs details. jobs_ids: {jobs_ids}", jobs_ids=jobs_ids)
        return [
            ClientJobDetails.from_job_details(job, qedma_observable_model)
            for job in self._get_jobs(
                jobs_ids, include_circuits=include_circuits, include_results=include_results
            )
        ]

    def list_jobs(self, skip: int = 0, limit: int = 50) -> list[models.JobDetails]:
        """
        Paginate jobs.
        :param skip: How many jobs to skip.
        :param limit: Maximum amount of jobs to return.
        :return: The list of requested jobs.
        """
        self.logger.info(
            "Listing jobs details. skip: [{skip}], limit: [{limit}]", skip=skip, limit=limit
        )

        response = requests.get(
            url=f"{self.uri}/jobs/list",
            params=[("skip", skip), ("limit", limit)],
            headers=self._headers,
            timeout=self.timeout,
        )

        self._raise_for_status(response)

        return GetJobsDetailsResponse.model_validate_json(response.content).jobs

    def register_qpu_token(self, token: str) -> None:
        """
        registers the QPU vendor token.
        :param token: The vendor token.
        """

        response = requests.post(
            url=f"{self.uri}/qpu-token",
            data=RegisterQpuTokenRequest(qpu_token=token).model_dump_json(),
            headers=self._headers,
            timeout=30,
        )

        self._raise_for_status(response)

    def unregister_qpu_token(self) -> None:
        """
        Unregisters a vendor token for an account.
        """

        response = requests.delete(
            url=f"{self.uri}/qpu-token",
            headers=self._headers,
            timeout=30,
        )

        self._raise_for_status(response)

    def _get_jobs(
        self,
        jobs_ids: list[str],
        *,
        include_circuits: bool = False,
        include_results: bool = False,
    ) -> list[models.JobDetails]:
        response = requests.get(
            url=f"{self.uri}/jobs",
            params=[
                ("ids", ",".join(jobs_ids)),
                ("include_circuits", include_circuits),
                ("include_results", include_results),
            ],
            headers=self._headers,
            timeout=self.timeout,
        )

        self._raise_for_status(response)

        jobs = GetJobsDetailsResponse.model_validate_json(response.content).jobs
        if not jobs:
            raise QedmaServerError("No jobs found")

        return jobs

    def _wait_for_status(  # pylint: disable=too-many-arguments
        self,
        job_id: str,
        statuses: set[models.JobStatus],
        interval: datetime.timedelta,
        timeout: datetime.timedelta | None,
        *,
        include_circuits: bool = False,
        include_results: bool = False,
        log_intermediate_results: bool = False,
    ) -> models.JobDetails:
        job = self._get_jobs(
            [job_id], include_circuits=include_circuits, include_results=include_results
        )[0]

        start = datetime.datetime.now()
        intermediate_results = None
        while job.status not in statuses:
            if timeout is not None and datetime.datetime.now() - start < timeout:
                raise TimeoutError("The given time out passed!")

            time.sleep(interval.total_seconds())
            job = self._get_jobs(
                [job_id], include_circuits=include_circuits, include_results=include_results
            )[0]

            if log_intermediate_results and job.intermediate_results:
                if job.intermediate_results != intermediate_results:
                    intermediate_results = job.intermediate_results
                    self.logger.info(
                        "[{job_id}] Intermediate results: [{results}]",
                        job_id=job_id,
                        results=job.intermediate_results,
                    )

        return job

    def wait_for_time_estimation(
        self,
        job_id: str,
        *,
        interval: datetime.timedelta = STATUS_POLLING_INTERVAL,
        max_poll_time: datetime.timedelta | None = None,
    ) -> datetime.timedelta | None:
        """
        Wait until a job reaches the time-estimation part, and get the estimation.

        :param job_id: The ID of the job.
        :param interval: The interval between two polls. Defaults to 10 seconds.
        :param max_poll_time: Max time until a timeout. If left empty, the method
        will return only when the job finishes.
        :return: The time estimation of the job.
        :raises: `TimeoutError` if max_poll_time passed.
        """
        job = self._wait_for_status(
            job_id,
            {
                models.JobStatus.ESTIMATED,
                models.JobStatus.RUNNING,
                models.JobStatus.SUCCEEDED,
                models.JobStatus.FAILED,
                models.JobStatus.CANCELLED,
            },
            interval,
            max_poll_time,
        )
        client_job = ClientJobDetails.from_job_details(job)

        self._print_warnings_and_errors(client_job)

        time_est = client_job.empirical_qpu_time_estimation
        time_est_desc = "Empirical"
        if time_est is None:
            time_est = client_job.analytical_qpu_time_estimation
            time_est_desc = "Analytical"

        if time_est is not None:
            self.logger.info(
                "[{job_id}] {time_est_desc} time estimation: [{time_est} minutes]",
                job_id=job_id,
                time_est=time_est.total_seconds() // 60,
                time_est_desc=time_est_desc,
            )

        return time_est

    def wait_for_job_complete(
        self,
        job_id: str,
        *,
        interval: datetime.timedelta = STATUS_POLLING_INTERVAL,
        max_poll_time: datetime.timedelta | None = None,
        qedma_observable_model: bool = False,
    ) -> ClientJobDetails:
        """
        Wait until the job finishes, and get the results. While the job is running,
        this function also prints the job's current step and intermediate results

        :param job_id: The ID of the job.
        :param interval: The interval between two polls. Defaults to 10 seconds.
        :param max_poll_time: Max time until a timeout. If left empty, the method
        will return only when the job finishes.
        :param qedma_observable_model: Whether to return the results with Qedma's observable model,
         or Qiskit SparsePauliOp.
        :return: The details of the job, including its results.
        :raises: `TimeoutError` if max_poll_time passed.
        """
        stop_event = threading.Event()
        progress_polling_thread = threading.Thread(
            target=self._progress_listener,
            kwargs={
                "sampling_interval": PROGRESS_POLLING_INTERVAL.total_seconds(),
                "print_interval": interval.total_seconds(),
                "job_id": job_id,
                "stop_event": stop_event,
            },
            daemon=True,
        )
        progress_polling_thread.start()

        try:
            job = self._wait_for_status(
                job_id,
                {
                    models.JobStatus.SUCCEEDED,
                    models.JobStatus.FAILED,
                    models.JobStatus.CANCELLED,
                },
                interval,
                max_poll_time,
                include_results=True,
                log_intermediate_results=True,
            )
            client_job = ClientJobDetails.from_job_details(job, qedma_observable_model)
        finally:
            stop_event.set()
            progress_polling_thread.join()

        self._print_warnings_and_errors(client_job)

        results = client_job.results
        self.logger.info(
            "[{job_id}] Final results: [{results}]",
            job_id=job_id,
            results=results,
        )

        return client_job

    def _progress_listener(
        self,
        sampling_interval: float,
        print_interval: float,
        job_id: str,
        stop_event: threading.Event,
    ) -> None:
        last_time = time.monotonic()
        next_step_idx = 0

        while True:
            job = self._get_jobs([job_id], include_circuits=False, include_results=False)[0]

            if job.progress and job.progress.steps:
                new_steps_count = len(job.progress.steps)

                if time.monotonic() - last_time > print_interval or new_steps_count > next_step_idx:
                    last_time = time.monotonic()

                    if new_steps_count > next_step_idx:
                        new_steps = job.progress.steps[next_step_idx:]
                        next_step_idx = new_steps_count
                        for step in new_steps:
                            self.logger.info(f"[{job.job_id}] step: [{step.name}]")

            # We break here instead in the while loop because we want to print any steps
            # that may have been added during the last sampling interval
            if stop_event.is_set():
                break
            time.sleep(sampling_interval)

    def _raise_for_status(self, response: requests.Response) -> None:
        http_error_msg = ""
        if isinstance(response.reason, bytes):
            # We attempt to decode utf-8 first because some servers choose to
            # localize their reason strings. If the string isn't utf-8, we fall
            # back to iso-8859-1 for all other encodings. (See PR #3538)
            try:
                reason = response.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = response.reason.decode("iso-8859-1")
        else:
            reason = response.reason

        if 400 <= response.status_code < 500:
            http_error_msg = (
                f"{response.status_code} Client Error: {reason} for url: {response.url}"
            )

        elif 500 <= response.status_code < 600:
            http_error_msg = (
                f"{response.status_code} Server Error: {reason} for url: {response.url}"
            )

        if http_error_msg:
            if not response.content:
                raise QedmaServerError(http_error_msg)

            try:
                details = response.json().get("detail")
            except json.JSONDecodeError:
                raise QedmaServerError(http_error_msg)  # pylint: disable=raise-missing-from

            self.logger.error(
                "Qedma server error: {http_error_msg}. Details: {details}",
                http_error_msg=http_error_msg,
                details=details,
            )
            raise QedmaServerError(http_error_msg, details=details)

    def _print_warnings_and_errors(self, job_details: ClientJobDetails) -> None:
        if job_details.warnings:
            for w in job_details.warnings:
                self.logger.warning(w)

        if job_details.errors:
            if len(job_details.errors) == 1:
                self.logger.error(
                    "Job creation encountered an error: {err}.", err=job_details.errors[0]
                )
            else:
                self.logger.error(
                    "Job creation encountered multiple errors: {errs}.", errs=job_details.errors
                )

    def _config_loguru(self) -> None:
        if sys.stderr or sys.stdout:
            self.logger.remove()  # Note that this affects anyone using loguru.logger
            if sys.stdout:
                self.logger.add(
                    sys.stdout,
                    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}",
                    filter=lambda record: record["extra"].get("scope") == self._logger_scope
                    and record["level"].no <= self.logger.level("INFO").no,
                )
            if sys.stderr:
                self.logger.add(
                    sys.stderr,
                    filter=lambda record: record["extra"].get("scope") != self._logger_scope,
                )
                self.logger.add(
                    sys.stderr,
                    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {message}",
                    filter=lambda record: record["extra"].get("scope") == self._logger_scope
                    and record["level"].no > self.logger.level("INFO").no,
                )
