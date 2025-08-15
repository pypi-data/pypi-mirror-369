from typing import Optional

from planqk.quantum.sdk.backend import PlanqkBackend
from planqk.quantum.sdk.client.client import _PlanqkClient
from planqk.quantum.sdk.client.job_dtos import JobDto
from planqk.quantum.sdk.client.model_enums import Provider
from planqk.quantum.sdk.qiskit import PlanqkQiskitJob
from planqk.quantum.sdk.qiskit.providers.aws.aws_qiskit_job import PlanqkAwsQiskitJob
from planqk.quantum.sdk.qiskit.providers.azure.azure_qiskit_job import PlanqkAzureQiskitJob
from planqk.quantum.sdk.qiskit.providers.qryd.qryd_qiskit_job import PlanqkQrydQiskitJob
from planqk.quantum.sdk.qiskit.providers.qudora.qudora_sim_job import PlanqkQudoraQiskitJob


class PlanqkQiskitJobFactory:
    @staticmethod
    def create_job(backend: Optional[PlanqkBackend], job_id: Optional[str] = None, job_details: Optional[JobDto] = None,
                   planqk_client: Optional[_PlanqkClient] = None) -> PlanqkQiskitJob:

        provider = PlanqkQiskitJobFactory._get_provider(backend, job_details)

        if not provider:
            raise ValueError("Provider information is missing. Either 'backend' or 'job_details' with the 'provider' attribute must be specified.")

        if provider == Provider.AWS:
            return PlanqkAwsQiskitJob(backend, job_id, job_details, planqk_client)
        elif provider == Provider.AZURE:
            return PlanqkAzureQiskitJob(backend, job_id, job_details, planqk_client)
        elif provider == Provider.QRYD:
            return PlanqkQrydQiskitJob(backend, job_id, job_details, planqk_client)
        elif provider == Provider.QUDORA:
            return PlanqkQudoraQiskitJob(backend, job_id, job_details, planqk_client)
        else:
            return PlanqkQiskitJob(backend, job_id, job_details, planqk_client)

    @staticmethod
    def _get_provider(backend, job_details):
        if backend:
            provider = backend.backend_info.provider
        else:
            provider = job_details.provider if job_details else None
        return provider