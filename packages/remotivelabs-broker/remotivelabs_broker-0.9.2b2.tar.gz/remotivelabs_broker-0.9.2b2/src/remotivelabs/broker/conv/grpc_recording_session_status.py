from __future__ import annotations

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.recording_session.mode import Mode
from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat
from remotivelabs.broker.recording_session.status import RecordingSessionStatus


def status_from_grpc(status: recordingsession__api__pb2.RecordingSessionStatus) -> RecordingSessionStatus:
    which = status.WhichOneof("status")
    return RecordingSessionStatus(
        path=status.path,
        error_message=status.errorMessage if which == "errorMessage" else None,
        mode=Mode(status.mode) if which == "mode" else None,
        offset=PlaybackOffset(status.offset.offsetTime),
        repeat=PlaybackRepeat(
            cycle_start_time=status.repeat.cycleStartTime,
            cycle_end_time=status.repeat.cycleEndTime,
        ),
    )


def status_to_grpc(status: RecordingSessionStatus) -> recordingsession__api__pb2.RecordingSessionStatus:
    assert status.mode or status.error_message, "either mode or error_message must be set (oneof)"

    return recordingsession__api__pb2.RecordingSessionStatus(
        path=status.path,
        offset=recordingsession__api__pb2.PlaybackOffset(offsetTime=status.offset.offset_time),
        repeat=recordingsession__api__pb2.PlaybackRepeat(
            cycleStartTime=status.repeat.cycle_start_time, cycleEndTime=status.repeat.cycle_end_time
        ),
        mode=status.mode.name if status.mode else None,
        errorMessage=status.error_message if status.error_message else None,
    )
