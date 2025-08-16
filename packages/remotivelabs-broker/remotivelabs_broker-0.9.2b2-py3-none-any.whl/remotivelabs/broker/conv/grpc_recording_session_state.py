from __future__ import annotations

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.recording_session.mode import Mode
from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat
from remotivelabs.broker.recording_session.state import RecordingSessionState


def state_from_grpc(state: recordingsession__api__pb2.RecordingSessionState) -> RecordingSessionState:
    return RecordingSessionState(
        path=state.path,
        mode=Mode(state.mode),
        offset=PlaybackOffset(state.offset.offsetTime),
        repeat=PlaybackRepeat(
            cycle_start_time=state.repeat.cycleStartTime,
            cycle_end_time=state.repeat.cycleEndTime,
        ),
    )


def state_to_grpc(self) -> recordingsession__api__pb2.RecordingSessionState:
    return recordingsession__api__pb2.RecordingSessionState(
        path=self.path,
        mode=self.mode.value,
        offset=recordingsession__api__pb2.PlaybackOffset(offsetTime=self.offset.offset_time),
        repeat=recordingsession__api__pb2.PlaybackRepeat(
            cycleStartTime=self.repeat.cycle_start_time, cycleEndTime=self.repeat.cycle_end_time
        ),
    )
