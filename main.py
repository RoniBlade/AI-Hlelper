import json
import queue
import threading
import logging

import config as cfg
import sounddevice as sd
import numpy as np
import webrtcvad

from vosk import Model, KaldiRecognizer, SetLogLevel

from RingBuffer import RingBuffer
from SpeechDetector import SpeechDetector

SetLogLevel(-1)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

log = logging.getLogger("main")

q = queue.Queue(maxsize=cfg.QUEUE_MAXSIZE)
transcribe_queue = queue.Queue(maxsize=cfg.QUEUE_MAXSIZE)

save_event = threading.Event()

vosk_model = Model("vosk-model-small-ru-0.4")
rec = KaldiRecognizer(vosk_model, cfg.SAMPLE_RATE, cfg.GRAMMAR)

vad = webrtcvad.Vad(cfg.VAD_MODE)
ring = RingBuffer(size=cfg.BUF_SAMPLES)
speech_detector = SpeechDetector(
    ring=ring,
    start_speech_frames=cfg.START_SPEECH_FRAMES,
    end_silence_frames=cfg.END_SILENCE_FRAMES,
    pre_samples=cfg.PRE_SAMPLES,
)


def transcribe_worker():
    while True:
        audio_i16 = transcribe_queue.get()

        try:

            ok = rec.AcceptWaveform(audio_i16.tobytes())

            if ok:
                text = (json.loads(rec.Result()).get("text") or "").strip()
            else:
                text = (json.loads(rec.FinalResult()).get("text") or "").strip()

            log.info("%s", text)
        except Exception:
            log.exception("ASR failed")
        finally:
            transcribe_queue.task_done()


def cb(indata, frames, time_info, status):
    one_frame = indata[:, 0].copy()
    try:
        q.put_nowait(one_frame)
    except queue.Full:
        pass


threading.Thread(target=transcribe_worker, daemon=True).start()

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
                try:
                    transcribe_queue.put_nowait(phrase_audio)
                except queue.Full:
                    log.warning("transcribe_queue full: dropped phrase")
    except KeyboardInterrupt:
        print("\nStopped")
