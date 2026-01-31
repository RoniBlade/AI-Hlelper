# =========================
# Audio format
# =========================
SAMPLE_RATE = 16_000  # Hz
CHANNELS = 1  # mono

# Frame (chunk) settings
FRAME_MS = 20  # ms per frame
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # samples per frame

# =========================
# Ring buffer (history)
# =========================
BUF_SEC = 2
BUF_SAMPLES = SAMPLE_RATE * BUF_SEC

# =========================
# VAD (speech detection)
# =========================
VAD_MODE = 2  # 0..3 (0 мягче, 3 агрессивнее)

# Start/stop phrase thresholds
START_SPEECH_FRAMES = 3  # сколько подряд "speech", чтобы стартовать запись
END_SILENCE_FRAMES = 40  # сколько подряд "silence", чтобы закончить запись

# Pre-roll (добавить немного звука ДО старта фразы)
PRE_ROLL_MS = 300
PRE_SAMPLES = SAMPLE_RATE * PRE_ROLL_MS // 1000
PRE_ROLL_FRAMES = PRE_ROLL_MS // FRAME_MS

# =========================
# Runtime buffers / queue
# =========================
QUEUE_MAXSIZE = 200  # очередь фреймов от callback -> main loop

# (Если DURATION_SEC реально нигде не используется — лучше убрать)
DURATION_SEC = 5

LANGUAGE = "ru"
WHISPER_MODEL = "base"
