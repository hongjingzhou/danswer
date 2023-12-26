import uvicorn
from fastapi import FastAPI

from tinyfish.imp import sync_mgr
from tinyfish.imp.models import ConnectorTfTaskStartRequest, ConnectorTfTaskStartResponse, ConnectorTaskTfCallbackType
from tinyfish.imp.models import ConnectorTfTaskStopRequest, ConnectorTfTaskStopResponse

app = FastAPI(docs_url="/api/docs")


@app.post("/start")
async def start_sync(req: ConnectorTfTaskStartRequest) -> ConnectorTfTaskStartResponse:
    if req.callback_url is None:
        req.callback_url = "/demo_callback"

    sync_id = sync_mgr.sync_start(req)
    if sync_id is None:
        return ConnectorTfTaskStartResponse(sync_id=None, error="failed to start sync")

    return ConnectorTfTaskStartResponse(sync_id=sync_id)


@app.post("/stop")
async def stop_sync(req: ConnectorTfTaskStopRequest) -> ConnectorTfTaskStopResponse:
    sync_mgr.sync_stop(req)
    return ConnectorTfTaskStopResponse(success=True)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8099)
