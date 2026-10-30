import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 14.8
CPS = 22.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * DUR) + SR)

BUBBLES = [(3.0, "Hi! I'm Byte.\nNeed a hand with this?"), (5.9, "Hello...?\nIs this thing on?"),
           (7.5, "Idea! This page\nneeds a title."), (9.9, "Want me to email\nit to someone?"),
           (11.9, "...no? Okay."), (13.2, "Bye for now!")]
TAPS = [5.6 + 0.4 * k for k in range(4)]


def add(t0, sig, gain=1.0):
    i = int(t0 * SR)
    if i < 0:
        return
    n = min(len(sig), len(out) - i)
    out[i:i + n] += sig[:n] * gain


def tt(d):
    return np.arange(int(d * SR)) / SR


def lowpass(x, fc, order=3):
    b, a = butter(order, fc / (SR / 2), 'low')
    return lfilter(b, a, x)


def bandpass(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band')
    return lfilter(b, a, x)


def tone(freqs, d, wave='sine', env_decay=6.0, attack=0.004):
    t = tt(d)
    f = np.broadcast_to(freqs, t.shape) if np.isscalar(freqs) else freqs
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave == 'sine':
        s = np.sin(ph)
    elif wave == 'tri':
        s = 2 / np.pi * np.arcsin(np.sin(ph))
    else:
        s = np.tanh(3 * np.sin(ph)) * 0.8
    env = np.exp(-env_decay * t) * np.minimum(1, t / attack)
    return s * env


def click():
    n = rng.standard_normal(int(0.025 * SR))
    n = bandpass(n, 1800, 6000) * np.exp(-tt(0.025) * 160)
    return n * 0.6


def boing(d=0.5):
    t = tt(d)
    f = 170 * (1 + 1.6 * np.exp(-7 * t)) * (1 + 0.25 * np.sin(2 * np.pi * 15 * t) * np.exp(-3 * t))
    return tone(f, d, 'sine', 4.5)


def thud():
    t = tt(0.16)
    f = 120 * np.exp(-12 * t) + 55
    s = tone(f, 0.16, 'sine', 18)
    n = lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 40) * 0.5
    return s + n


def pop(f0=420, f1=950):
    d = 0.09
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d)
    return tone(f, d, 'sine', 30) * 0.8


def blip(f):
    d = 0.05
    return tone(np.full(int(d * SR), f), d, 'tri', 38, 0.003) * 0.55


def bell(f=1320, d=1.0):
    t = tt(d)
    s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-4 * t)
         + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-9 * t))
    return s * np.exp(-4.5 * t) * np.minimum(1, t / 0.003) * 0.5


def whoosh(d=0.35, up=True):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out_s = np.zeros_like(n)
    seg = 12
    for k in range(seg):
        a, b = int(k * len(t) / seg), int((k + 1) * len(t) / seg)
        fc = 500 + 3500 * ((k / seg) if up else (1 - k / seg))
        out_s[a:b] = bandpass(n, fc * 0.7, fc * 1.4)[a:b]
    env = np.sin(np.pi * t / d) ** 2
    return out_s * env * 1.4


def slide(f0, f1, d, wave='tri', decay=3.0):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d)
    return tone(f, d, wave, decay)


def poof():
    t = tt(0.3)
    n = lowpass(rng.standard_normal(len(t)), 1800) * np.exp(-9 * t)
    return n * 1.2


def chime(f):
    return bell(f, 0.5) * 0.45


# typing clicks while the first sentence is typed
for k in range(22):
    add(0.05 + k * 0.045 + rng.uniform(0, 0.015), click(), rng.uniform(0.5, 0.9))

# pop-in
add(1.0, whoosh(0.3, True), 0.3)
add(1.12, boing(0.55), 0.6)
add(1.88, thud(), 0.45)

# bubbles: pop and talking blips
pitches = [520, 590, 660, 740, 590, 700]
for s, txt in BUBBLES:
    add(s, pop(), 0.7)
    chars = [c for c in txt if c not in ' \n']
    i = 0
    for k, c in enumerate(txt):
        if c in ' \n':
            continue
        if i % 2 == 0:
            add(s + 0.2 + k / CPS, blip(pitches[(i // 2 * 7 + len(txt)) % len(pitches)] * (0.85 if '?' in txt else 1)), 0.5)
        i += 1

# blink ticks are silent; look-around: tiny swish
add(2.0, whoosh(0.18, True), 0.12)
add(2.5, whoosh(0.18, False), 0.12)

# tapping on the window
for tp in TAPS:
    add(tp, thud(), 0.8)

# lightbulb idea
add(7.3, bell(1568, 1.0), 0.8)
add(7.33, bell(2093, 0.7), 0.35)
# title typing
for k in range(14):
    add(8.2 + k * 0.057, click(), 0.7)
# sparkle
for j, f in enumerate([2093, 2637, 3136, 3951]):
    add(8.7 + j * 0.07, chime(f), 0.5)

# envelope
add(9.6, whoosh(0.3, True), 0.5)
add(9.85, pop(600, 1100), 0.4)
# envelope drops
add(11.5, slide(900, 200, 0.5, 'sine', 3.5), 0.45)

# sad womp womp
add(11.7, slide(330, 270, 0.4, 'tri', 2.2), 0.7)
add(12.15, slide(280, 190, 0.55, 'tri', 2.0), 0.7)
# tear drip
add(11.85, slide(1400, 700, 0.12, 'sine', 14), 0.3)

# hopeful hops
add(12.9, slide(300, 700, 0.14, 'sine', 12), 0.6)
add(13.1, slide(350, 800, 0.14, 'sine', 12), 0.6)
add(13.3, bell(1760, 0.5), 0.4)

# wave: two friendly notes
add(13.5, slide(660, 880, 0.12, 'tri', 10), 0.4)
add(13.7, slide(880, 990, 0.12, 'tri', 10), 0.4)

# poof
add(14.0, poof(), 0.8)
for j, f in enumerate([3136, 2637, 2093, 1568]):
    add(14.03 + j * 0.07, chime(f), 0.5)

m = np.max(np.abs(out))
out = out / m * 0.85
out[int((DUR - 0.15) * SR):] *= np.linspace(1, 0, len(out[int((DUR - 0.15) * SR):]))
out = out[:int(DUR * SR)]
wavfile.write('byte_sfx.wav', SR, (out * 32767).astype(np.int16))
print('wrote', len(out) / SR, 's')
