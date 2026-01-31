import queue
import threading
import logging

import config as cfg
import sounddevice as sd
import numpy as np
import webrtcvad
import whisper

from RingBuffer import RingBuffer
from SpeechDetector import SpeechDetector

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

q = queue.Queue(maxsize=cfg.QUEUE_MAXSIZE)
save_event = threading.Event()

vad = webrtcvad.Vad(cfg.VAD_MODE)
model = whisper.load_model("base")
ring = RingBuffer(size=cfg.BUF_SAMPLES)
speech_detector = SpeechDetector(
    ring=ring,
    start_speech_frames=cfg.START_SPEECH_FRAMES,
    end_silence_frames=cfg.END_SILENCE_FRAMES,
    pre_samples=cfg.PRE_SAMPLES,
)

def wait_enter():
    while True:
        input()
        save_event.set()


def cb(indata, frames, time_info, status):
    one_frame = indata[:, 0].copy()
    try:
        q.put_nowait(one_frame)
    except queue.Full:
        pass


threading.Thread(target=wait_enter, daemon=True).start()

print("Start...")

with sd.InputStream(samplerate=cfg.SAMPLE_RATE, channels=cfg.CHANNELS, dtype=np.int16, blocksize=cfg.FRAME_SAMPLES,
                    callback=cb):
    try:
        while True:
            frame = q.get()
            ring.write(frame)

            is_speech = vad.is_speech(frame.tobytes(), cfg.SAMPLE_RATE)
            phrase_audio = speech_detector.update(frame, is_speech)

            if phrase_audio is not None:
                audio_f32 = phrase_audio.astype(np.float32) / 32768.0
                result = model.transcribe(audio_f32, fp16=False, language=cfg.LANGUAGE)
                print(result["text"])
    except KeyboardInterrupt:
        print("\nStopped")
