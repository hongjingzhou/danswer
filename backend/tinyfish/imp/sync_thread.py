import threading
import time
import uuid
from typing import Any, Callable

from danswer.configs.constants import DocumentSource
from danswer.connectors.factory import instantiate_connector
from danswer.connectors.interfaces import LoadConnector, PollConnector, EventConnector
from danswer.connectors.models import InputType, Document
from tinyfish.imp.models import ConnectorTaskTfCallbackType, ConnectorTaskTfCredentialsCallback, \
    ConnectorTaskTfDocumentCallback, ConnectorTaskTfFinishedCallback


def _merge_split_docs(doc: Document) -> str:
    s = ''
    for section in doc.sections:
        s += section.text
    return s


class TinyFishSyncThread(threading.Thread):
    def __init__(self,
                 source: str,
                 input_type: str,
                 credentials: dict[str, Any],
                 config: dict[str, Any],
                 last_run_time: float,
                 event_callback: Callable[[ConnectorTaskTfCallbackType, Any], None]):
        super().__init__()

        self.source = source
        self.input_type = input_type
        self.credentials = credentials
        self.config = config
        self.last_run_time = last_run_time
        self.event_callback = event_callback
        self.run_time = time.time()
        self.sync_id = str(uuid.uuid4())
        self.cancelled = False

    def stop(self):
        self.cancelled = True

    def run(self):
        err = None
        try:
            self.work()
        except Exception as e:
            print(e)
            err = str(e)

        if self.cancelled:
            err = "Cancelled"

        self.on_sync_done(err)

    def work(self):
        connector, new_credentials = instantiate_connector(
            source=DocumentSource(self.source),
            input_type=InputType(self.input_type),
            connector_specific_config=self.config,
            credentials=self.credentials)
        new_credentials = connector.load_credentials(new_credentials or self.credentials)
        if new_credentials is not None and new_credentials != self.credentials:
            self.on_credential_changed(new_credentials)

        if self.input_type == InputType.LOAD_STATE:
            assert isinstance(connector, LoadConnector)
            generator = connector.load_from_state()
        elif self.input_type == InputType.POLL:
            assert isinstance(connector, PollConnector)
            generator = connector.poll_source(0, 0)
        elif self.input_type == InputType.EVENT:
            assert isinstance(connector, EventConnector)
            generator = connector.handle_event(0)
        else:
            raise ValueError(f"Invalid input_type={self.input_type}")

        for batch_docs in generator:
            if self.cancelled:
                break

            for doc in batch_docs:
                if self.cancelled:
                    break
                self.on_doc_fetched(doc)

            if self.cancelled:
                break

    def on_credential_changed(self, new_credentials: dict[str, Any]):
        event_type = ConnectorTaskTfCallbackType.CREDENTIAL_CHANGED
        data = ConnectorTaskTfCredentialsCallback(
            sync_id=self.sync_id,
            credentials=new_credentials,
        )
        self.event_callback(event_type, data)

    def on_doc_fetched(self, doc: Document):
        event_type = ConnectorTaskTfCallbackType.DOCUMENT
        data = ConnectorTaskTfDocumentCallback(
            sync_id=self.sync_id,
            meta=doc.metadata,
            data=_merge_split_docs(doc),
        )
        self.event_callback(event_type, data)

    def on_sync_done(self, error: str | None):
        event_type = ConnectorTaskTfCallbackType.FINISHED
        data = ConnectorTaskTfFinishedCallback(
            sync_id=self.sync_id,
            success=error is None,
            error=error,
            run_time=self.run_time,
        )

        print("on_sync_done", data)
        self.event_callback(event_type, data)

