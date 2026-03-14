import numpy as np


class RingBuffer:
    def __init__(self, size: int, dtype=np.int16):
        self.buf = np.zeros(size, dtype=dtype)
        self.pos = 0

    def write(self, frame: np.ndarray) -> None:
        n = len(frame)
        end = n + self.pos

        if end <= len(self.buf):
            self.buf[self.pos:end] = frame
        else:
            first = len(self.buf) - self.pos
            self.buf[self.pos:] = frame[:first]
            self.buf[:end - len(self.buf)] = frame[first:]

        self.pos = (self.pos + n) % len(self.buf)

    def snapshot(self) -> np.ndarray:
        return np.concatenate([self.buf[self.pos:], self.buf[:self.pos]])

    def last(self, n_samples: int) -> np.ndarray:
        snap = self.snapshot()
        return snap[-n_samples:]
