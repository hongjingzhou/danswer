from enum import Enum
from typing import Any
from pydantic import BaseModel


# the below is for connector sync task,
# must be consistent between danswner backend and tinyfish backend
class ConnectorTfTaskStartRequest(BaseModel):
    # github, notion, google_drive ect.
    connector: str
    # load_state, poll, event
    sync_type: str
    credentials: dict[str, Any]
    config: dict[str, Any]
    last_run_time: float
    callback_url: str


class ConnectorTfTaskStartResponse(BaseModel):
    # uuid for this task, used to stop task
    sync_id: str
    error: str | None = None


class ConnectorTfTaskStopRequest(BaseModel):
    sync_id: str


class ConnectorTfTaskStopResponse(BaseModel):
    success: bool
    error: str | None = None


class ConnectorTaskTfCallbackType(Enum):
    # data will be ConnectorTaskTfDocument
    FINISHED = 'finished'

    # data will be ConnectorTaskTfDocument
    DOCUMENT = 'document'

    # data will be ConnectorTaskTfConfig
    CREDENTIAL_CHANGED = 'credentials_changed'


class ConnectorTaskTfDocumentCallback(BaseModel):
    sync_id: str
    meta: dict[str, Any]
    data: str


class ConnectorTaskTfCredentialsCallback(BaseModel):
    sync_id: str
    credentials: dict[str, Any]


class ConnectorTaskTfFinishedCallback(BaseModel):
    sync_id: str
    success: bool
    error: str | None = None
    run_time: float | None = None

