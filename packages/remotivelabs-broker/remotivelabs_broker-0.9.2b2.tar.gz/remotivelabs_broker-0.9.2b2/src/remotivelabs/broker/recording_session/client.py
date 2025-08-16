from __future__ import annotations

import logging
from typing import AsyncIterator

from remotivelabs.broker._generated import common_pb2
from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.client import BrokerClient
from remotivelabs.broker.conv.grpc_recording_session_file import file_from_grpc
from remotivelabs.broker.conv.grpc_recording_session_state import state_to_grpc
from remotivelabs.broker.conv.grpc_recording_session_status import status_from_grpc
from remotivelabs.broker.recording_session.file import File
from remotivelabs.broker.recording_session.state import RecordingSessionState
from remotivelabs.broker.recording_session.status import RecordingSessionStatus

_logger = logging.getLogger(__name__)


class RecordingSessionClient(BrokerClient):
    """
    TODO: We probably dont want to inherit from BrokerClient, but rather use composition to hide functionality not relevant for recording
    session operations. However, this will do for now.
    """

    async def __aenter__(self) -> RecordingSessionClient:
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await super().__aexit__(exc_type, exc_value, traceback)

    async def list_recording_files(self, path: str | None = None) -> list[File]:
        """
        List recording files in a directory.

        Args:
            path: Optional path to the subdirectory containing the recording files.
        """
        res = await self._recording_session_service.ListRecordingFiles(recordingsession__api__pb2.FileListingRequest(path=path))
        return [file_from_grpc(file) for file in res.files]

    def status(self) -> AsyncIterator[list[RecordingSessionStatus]]:
        """
        Get continuous status of all open recording sessions.
        """
        stream = self._recording_session_service.Status(common_pb2.Empty())

        async def async_generator() -> AsyncIterator[list[RecordingSessionStatus]]:
            async for items in stream:
                status_list = [status_from_grpc(item) for item in items]
                if status_list:
                    yield status_list

        return async_generator()

    async def set_state(self, state: RecordingSessionState) -> RecordingSessionStatus:
        """
        Set desired state of the recording session
        """
        grpc_state = state_to_grpc(state)
        res = await self._recording_session_service.SetState(grpc_state)
        return status_from_grpc(res)
