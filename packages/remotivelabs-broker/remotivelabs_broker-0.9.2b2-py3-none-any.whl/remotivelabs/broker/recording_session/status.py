from __future__ import annotations

from dataclasses import dataclass

from remotivelabs.broker.recording_session.mode import Mode
from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat


@dataclass
class RecordingSessionStatus:
    path: str
    offset: PlaybackOffset
    repeat: PlaybackRepeat
    mode: Mode | None = None
    error_message: str | None = None
