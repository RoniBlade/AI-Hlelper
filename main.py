import json
import queue
import threading
import logging
import os
import sys
import pystray
import config as cfg
import sounddevice as sd
import numpy as np
import webrtcvad
from PIL import Image, ImageDraw
from vosk import Model, KaldiRecognizer, SetLogLevel
from command_processor.command_dispatcher import CommandDispatcher
from ring_buffer import RingBuffer
from speech_detector import SpeechDetector

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

log = logging.getLogger("main")

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(".")

model_path = os.path.join(base_path, "model", "vosk-model-small-ru-0.22")

command_processor = CommandDispatcher()

SetLogLevel(-1)

q = queue.Queue(maxsize=cfg.QUEUE_MAXSIZE)
transcribe_queue = queue.Queue(maxsize=cfg.QUEUE_MAXSIZE)

save_event = threading.Event()

try:
    vosk_model = Model(model_path)
    rec_full = KaldiRecognizer(vosk_model, cfg.SAMPLE_RATE, command_processor.grammar_json)
    log.debug("Model loaded successfully.")
except Exception as e:
    log.error(f"Failed to load model: {e}")

vad = webrtcvad.Vad(cfg.VAD_MODE)
ring = RingBuffer(size=cfg.BUF_SAMPLES)
speech_detector = SpeechDetector(
    ring=ring,
    start_speech_frames=cfg.START_SPEECH_FRAMES,
    end_silence_frames=cfg.END_SILENCE_FRAMES,
    pre_samples=cfg.PRE_SAMPLES,
)

shutdown_event = threading.Event()

def transcribe_worker():
    while not shutdown_event.is_set():
        audio_i16 = transcribe_queue.get()
        try:
            rec_full.Reset()
            rec_full.AcceptWaveform(audio_i16.tobytes())
            res = json.loads(rec_full.FinalResult())
            log.debug(f"Recognition result: {res}")
            text = (res.get("text") or "").strip()
            command_processor.dispatch(text)
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

def create_tray_icon():
    icon_path = os.path.join(base_path, "icon.ico")
    if not os.path.exists(icon_path):
        log.error(f"Icon file {icon_path} not found.")
        return

    def on_quit(icon, item):
        shutdown_event.set()
        icon.stop()

    menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))

    icon = pystray.Icon("App", Image.open(icon_path), menu=menu)
    icon.run()

threading.Thread(target=transcribe_worker, daemon=True).start()
threading.Thread(target=create_tray_icon, daemon=True).start()

log.info("Start...")

with sd.InputStream(samplerate=cfg.SAMPLE_RATE, channels=cfg.CHANNELS, dtype=np.int16, blocksize=cfg.FRAME_SAMPLES,
                    callback=cb):
    try:
        while not shutdown_event.is_set():
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
        log.info("Stopped")
