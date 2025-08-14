import json
from typing import Optional, Dict, Set, Union

from pydantic import BaseModel, field_serializer

from planqk.quantum.sdk.client.model_enums import Provider, JobInputFormat, PlanqkSdkProvider


class JobDto(BaseModel):
    provider: Provider
    shots: int = 1
    backend_id: Optional[str] = None
    id: Optional[str] = None
    provider_job_id: Optional[str] = None
    session_id: Optional[str] = None
    input: Optional[Union[str, Dict]] = None
    input_format: Optional[JobInputFormat] = None
    input_params: Optional[Dict] = None
    error_data: Optional[dict] = None
    started_at: Optional[str] = None
    created_at: Optional[str] = None
    ended_at: Optional[str] = None
    name: Optional[str] = None
    tags: Optional[Set[str]] = None
    sdk_provider: Optional[PlanqkSdkProvider] = None

    @field_serializer('provider')
    def serialize_provider(self, provider: Provider) -> str:
        return provider.value

    @field_serializer('sdk_provider')
    def serialize_sdk_provider(self, sdk_provider: PlanqkSdkProvider) -> str:
        return sdk_provider.value if sdk_provider else None

    def __post_init__(self):
        if self.error_data is not None and isinstance(self.error_data, str):
            self.error_data = json.loads(self.error_data)
        if self.input_params is not None and isinstance(self.input_params, str):
            self.input_params = json.loads(self.input_params)


class JobSummary(BaseModel):
    id: str
    provider: Provider
    backend_id: str
    created_at: Optional[str] = None


class RuntimeJobParamsDto(BaseModel):
    program_id: str
    image: Optional[str] = None
    hgp: Optional[str]
    log_level: Optional[str] = None
    session_id: Optional[str] = None
    max_execution_time: Optional[int] = None
    start_session: Optional[bool] = False
    session_time: Optional[int] = None
