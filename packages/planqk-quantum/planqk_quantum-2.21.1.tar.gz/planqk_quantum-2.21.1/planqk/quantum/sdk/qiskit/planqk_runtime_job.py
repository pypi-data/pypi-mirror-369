import json
from datetime import datetime
from typing import Optional, Type, Any, Callable, Dict, Union, Sequence

from qiskit.providers import Backend, JobStatus
from qiskit_ibm_runtime import RuntimeJobMaxTimeoutError, RuntimeJobFailureError, RuntimeInvalidStateError
from qiskit_ibm_runtime.constants import DEFAULT_DECODERS
from qiskit_ibm_runtime.utils.result_decoder import ResultDecoder

from planqk.quantum.sdk.client.client import _PlanqkClient
from planqk.quantum.sdk.client.job_dtos import JobDto
from planqk.quantum.sdk.qiskit import PlanqkQiskitJob


class PlanqkRuntimeJob(PlanqkQiskitJob):

    def __init__(self, backend: Optional[Backend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None,
                 result_decoder: Optional[Union[Type[ResultDecoder], Sequence[Type[ResultDecoder]]]] = None,
                 planqk_client: Optional[_PlanqkClient] = None):
        super().__init__(backend, job_id, job_details, planqk_client=planqk_client)
        self._session_id = self._job_details.input_params.get('session_id', None)
        self._program_id = self._job_details.input_params.get('program_id', None)

        decoder = result_decoder or DEFAULT_DECODERS.get(self._program_id, None) or ResultDecoder
        if isinstance(decoder, Sequence):
            self._interim_result_decoder, self._final_result_decoder = decoder
        else:
            self._interim_result_decoder = self._final_result_decoder = decoder

    def interim_results(self, decoder: Optional[Type[ResultDecoder]] = None) -> Any:
        raise NotImplementedError("Interim results are not supported for PLANQK runtime jobs.")

    def _result(  # pylint: disable=arguments-differ
        self,
        timeout: Optional[float] = None,
        decoder: Optional[Type[ResultDecoder]] = None,
    ) -> Any:
        """Return the results of the job.

        Args:
            timeout: Number of seconds to wait for job.
            decoder: A :class:`ResultDecoder` subclass used to decode job results.

        Returns:
            Runtime job result.

        Raises:
            RuntimeJobFailureError: If the job failed.
            RuntimeJobMaxTimeoutError: If the job does not complete within given timeout.
            RuntimeInvalidStateError: If the job was cancelled, and attempting to retrieve result.
        """
        _decoder = decoder or self._final_result_decoder
        if self._result is None or (_decoder != self._final_result_decoder):
            self._wait_for_final_state(timeout=timeout)
            status = self._update_state()
            if status == JobStatus.ERROR:
                error_message = self._reason if self._reason else self._error_message
                if self._reason == "RAN TOO LONG":
                    raise RuntimeJobMaxTimeoutError(error_message)
                raise RuntimeJobFailureError(f"Unable to retrieve job result. {error_message}")
            if status is JobStatus.CANCELLED:
                raise RuntimeInvalidStateError(
                    "Unable to retrieve result for job {}. "
                    "Job was cancelled.".format(self.job_id())
                )

            result_raw = self._client.get_job_result(self.id)

            self._result = _decoder.decode(json.dumps(result_raw)) if result_raw else None
        return self._result

    def stream_results(
        self, callback: Callable, decoder: Optional[Type[ResultDecoder]] = None
    ) -> None:
        raise NotImplementedError("Result streaming is not supported for PLANQK runtime jobs.")

    def cancel_result_streaming(self) -> None:
        raise NotImplementedError("Canceling result streaming is not supported for PLANQK runtime jobs.")

    def logs(self) -> str:
        raise NotImplementedError("Logs are not supported for PLANQK runtime jobs.")

    def metrics(self) -> Dict[str, Any]:
        raise NotImplementedError("Metrics are not supported for PLANQK runtime jobs.")

    @property
    def image(self) -> str:
        """Return the runtime image used for the job.

        Returns:
            Runtime image: image_name:tag or "" if the default
            image is used.
        """
        raise NotImplementedError("Image is not supported for PLANQK runtime jobs.")

    @property
    def inputs(self) -> Dict:
        """Job input parameters.

        Returns:
            Input parameters used in this job.
        """
        raise NotImplementedError("Inputs are not supported for PLANQK runtime jobs.")

    @property
    def program_id(self) -> str:
        """Program ID.

        Returns:
            ID of the program this job is for.
        """
        return self._program_id

    @property
    def creation_date(self) -> Optional[datetime]:
        """Job creation date in local time.

        Returns:
            The job creation date as a datetime object, in local time, or
            ``None`` if creation date is not available.
        """
        raise NotImplementedError("Creation date is not supported for PLANQK runtime jobs.")

    @property
    def session_id(self) -> str:
        """Session ID.

        Returns:
            Job ID of the first job in a runtime session.
        """
        return self._session_id
