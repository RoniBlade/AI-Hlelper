from typing import Optional, List
import numpy as np

from RingBuffer import RingBuffer

import logging

log = logging.getLogger(__name__)


class SpeechDetector:

    def __init__(
            self,
            ring: RingBuffer,
            start_speech_frames: int,
            end_silence_frames: int,
            pre_samples: int,
            log_events: bool = True,
    ):
        self.ring = ring
        self.start_speech_frames = int(start_speech_frames)
        self.end_silence_frames = int(end_silence_frames)
        self.pre_samples = int(pre_samples)
        self.log_events = bool(log_events)

        self.speech_run = 0
        self.silence_run = 0
        self.recording = False
        self.frames: List[np.ndarray] = []

    def update(self, frame: np.ndarray, is_speech: bool) -> Optional[np.ndarray]:
        if is_speech:
            self.silence_run = 0
            self.speech_run += 1
        else:
            self.speech_run = 0
            self.silence_run += 1

        if not self.recording and self.speech_run >= self.start_speech_frames:
            log.info(">> START phrase")

            self.recording = True
            pre = self.ring.snapshot()[-self.pre_samples:]
            self.frames = [pre]

        if self.recording:
            self.frames.append(frame)

            if (not is_speech) and (self.silence_run >= self.end_silence_frames):
                self.recording = False
                phrase = np.concatenate(self.frames)
                self.frames = []
                self.silence_run = 0

                log.info("<< END phrase")

                return phrase

        return None

    def reset(self) -> None:
        self.speech_run = 0
        self.silence_run = 0
        self.recording = False
        self.frames = []
