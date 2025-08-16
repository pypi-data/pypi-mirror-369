from enum import Enum


class Mode(Enum):
    PLAY = 0
    """Playing a file."""
    PAUSE = 1
    """Playback is paused."""
    STOP = 2
    """Playback in stopped and will be played from beginning when restarted."""
    RECORD = 3
    """Recording a playback."""
    SEEK = 4
    """Seek to offset in a playback."""
    CLOSE = 5
    """Close the recording session."""
