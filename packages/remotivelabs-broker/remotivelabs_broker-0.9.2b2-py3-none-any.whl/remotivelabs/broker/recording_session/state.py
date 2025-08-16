from __future__ import annotations

from dataclasses import dataclass, field

from remotivelabs.broker.recording_session.mode import Mode
from remotivelabs.broker.recording_session.offset import PlaybackOffset
from remotivelabs.broker.recording_session.repeat import PlaybackRepeat


@dataclass
class RecordingSessionState:
    path: str
    mode: Mode
    offset: PlaybackOffset = field(default_factory=PlaybackOffset)
    repeat: PlaybackRepeat = field(default_factory=PlaybackRepeat)
