import json
from typing import Any

import requests
from tinyfish.imp.models import ConnectorTfTaskStartRequest, ConnectorTfTaskStopRequest, ConnectorTaskTfCallbackType
from tinyfish.imp.sync_thread import TinyFishSyncThread

global_sync_threads_map = {}
global_sync_callback_url_map = {}


def _sync_event_callback(event_type: ConnectorTaskTfCallbackType,
                         data: Any):
    print("sync_event_callback called")
    print(data)

    url = global_sync_callback_url_map.get(data.sync_id)
    if event_type == ConnectorTaskTfCallbackType.FINISHED:
        # remove the sync thread from the global map
        global_sync_threads_map.pop(data.sync_id, None)
        global_sync_callback_url_map.pop(data.sync_id, None)

    if url is None or url == "":
        return

    if url.endswith("/"):
        url = url[:-1]

    if event_type == ConnectorTaskTfCallbackType.FINISHED:
        url += "/finished"
    elif event_type == ConnectorTaskTfCallbackType.DOCUMENT:
        url += "/document"
    elif event_type == ConnectorTaskTfCallbackType.CREDENTIAL_CHANGED:
        url += "/credentials"
    else:
        return

    json_data = json.dumps(data, default=lambda o: o.__dict__)
    try:
        requests.post(url, data=json_data)
    except Exception as e:
        print(e)


def sync_start(request: ConnectorTfTaskStartRequest) -> str | None:
    try:
        thread = TinyFishSyncThread(request.connector,
                                    request.sync_type,
                                    request.credentials,
                                    request.config,
                                    request.last_run_time,
                                    _sync_event_callback)
        thread.start()

        global_sync_threads_map[thread.sync_id] = thread
        global_sync_callback_url_map[thread.sync_id] = request.callback_url
        return thread.sync_id
    except Exception as e:
        print(e)
    return None


def sync_stop(request: ConnectorTfTaskStopRequest):
    thread = global_sync_threads_map.pop(request.sync_id, None)
    if thread is None:
        return
    thread.stop()


if __name__ == "__main__":
    def main_test():
        from danswer.configs.constants import DocumentSource
        from danswer.connectors.models import InputType
        from danswer.connectors.web.connector import WEB_CONNECTOR_VALID_SETTINGS

        c = {
            "base_url": "https://tinyfish.io/",
            "web_connector_type": WEB_CONNECTOR_VALID_SETTINGS.RECURSIVE.value
        }
        request = ConnectorTfTaskStartRequest(
            connector=DocumentSource.WEB.value,
            sync_type=InputType.LOAD_STATE.value,
            credentials={},
            config=c,
            last_run_time=0,
            callback_url="",
        )

        sync_id = sync_start(request=request)
        print(sync_id)

        if sync_id is None:
            print("Failed to start sync")
            raise Exception("Failed to start sync")

        global_sync_threads_map.get(sync_id).join()
        print("Sync finished")


    main_test()
