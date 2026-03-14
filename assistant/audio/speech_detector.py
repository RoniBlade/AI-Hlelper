from typing import Optional, List
import numpy as np

from assistant import config as cfg

from assistant.audio.ring_buffer import RingBuffer

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
        self.recording_frames = 0
        self.recording = False
        self.frames: List[np.ndarray] = []
        self.ignore_until_silence = False

    def update(self, frame: np.ndarray, is_speech: bool) -> Optional[np.ndarray]:
        if is_speech:
            self.silence_run = 0
            self.speech_run += 1
        else:
            self.speech_run = 0
            self.silence_run += 1

        if self.silence_run >= self.end_silence_frames:
            self.ignore_until_silence = False

        if not self.recording and not self.ignore_until_silence and self.speech_run >= self.start_speech_frames:
            log.info(">> START phrase")

            self.recording = True
            self.recording_frames = 0
            pre = self.ring.snapshot()[-self.pre_samples:]
            self.frames = [pre]

        if self.recording:
            self.recording_frames += 1

            if self.recording_frames >= cfg.LONG_PHRASE_FRAMES:
                self.recording = False
                self.frames = []
                self.recording_frames = 0
                self.speech_run = 0
                self.ignore_until_silence = True

                return None

            self.frames.append(frame)

            if (not is_speech) and (self.silence_run >= self.end_silence_frames):
                self.recording = False
                phrase = np.concatenate(self.frames)
                self.frames = []
                self.silence_run = 0
                self.recording_frames = 0
                log.info("<< END phrase")
                return phrase

        return None

    def reset(self) -> None:
        self.speech_run = 0
        self.silence_run = 0
        self.recording_frames = 0
        self.recording = False
        self.frames = []
        self.ignore_until_silence = False
