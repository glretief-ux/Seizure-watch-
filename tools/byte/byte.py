import math, os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1280, 720, 2, 30
DUR = 14.8
HERE = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_f = {}


def font(sz, bold=False):
    k = (sz, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(FB if bold else F, int(sz * S))
    return _f[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def sstep(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def back(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


BODY = (91, 141, 239)
BODY_D = (52, 96, 196)
ARM = (74, 120, 214)
PLATE = (20, 33, 61)
EYE = (125, 249, 255)
CHEEK = (249, 168, 212)
YEL = (255, 209, 102)
INK = (31, 41, 55)
K = 1.6
CPS = 22.0

BUBBLES = [
    (3.0, 5.4, "Hi! I'm Byte.\nNeed a hand with this?"),
    (5.9, 7.1, "Hello...?\nIs this thing on?"),
    (7.5, 9.5, "Idea! This page\nneeds a title."),
    (9.9, 11.5, "Want me to email\nit to someone?"),
    (11.9, 12.8, "...no? Okay."),
    (13.2, 14.0, "Bye for now!"),
]

BODY_TEXT = [
    "The team met on Tuesday to review the",
    "progress so far. Most tasks are on track,",
    "but a few items still need an owner before",
    "the end of the month. Next steps are listed",
    "below, and everyone should add their notes.",
]
TAP_TIMES = [5.6 + 0.4 * k for k in range(4)]
BLINKS = [2.0, 4.6, 8.0, 10.3, 12.4, 13.5]


def keyinterp(keys, t, tr=0.25):
    cur = keys[0]
    prev = keys[0]
    for i, k in enumerate(keys):
        if k[0] <= t:
            cur = k
            prev = keys[i - 1] if i > 0 else k
    a = sstep((t - cur[0]) / tr)
    return tuple(lerp(p, c, a) for p, c in zip(prev[1:], cur[1:]))


LOOK = [(0, 0, 0), (2.0, 1, 0.3), (2.5, -1, -0.4), (2.9, 0, 0), (5.3, -1, 0), (7.0, 0, 0),
        (7.3, 0, -1), (9.4, 0, 0), (9.6, 0.8, -0.8), (11.4, 0, 0), (11.7, 0, 0.9), (12.8, 0, 0)]
HAND_R = [(0, 96, -48), (7.3, 100, -108), (9.4, 96, -48), (9.6, 98, -122), (11.6, 92, -34),
          (12.8, 96, -48), (13.2, 108, -124)]
HAND_L = [(0, -96, -48), (5.2, -108, -62), (6.9, -96, -48), (11.6, -92, -34), (12.8, -96, -48)]


def mood(t):
    if 8.35 <= t < 9.3 or 12.9 <= t < 13.9:
        return 'happy'
    if 11.7 <= t < 12.8:
        return 'sad'
    return 'normal'


def blink(t):
    for e in BLINKS:
        dt = t - e
        if 0 <= dt < 0.2:
            return 1 - abs(dt - 0.1) / 0.1
    return 0.0


def talking(t):
    for s, e, txt in BUBBLES:
        if s + 0.2 <= t < s + 0.2 + len(txt) / CPS + 0.2:
            return True
    return False


def byte_x(t):
    if 5.1 <= t < 5.6:
        return lerp(1020, 930, sstep((t - 5.1) / 0.5))
    if 5.6 <= t < 6.9:
        return 930
    if 6.9 <= t < 7.4:
        return lerp(930, 1020, sstep((t - 6.9) / 0.5))
    return 1020


def byte_vert(t):
    """returns (yoff, sx, sy, scale) ; yoff positive = lower."""
    if t < 1.0:
        return None
    if t < 1.9:
        p = (t - 1.0) / 0.9
        off = 380 * (1 - back(p))
        s = 0.14 * math.sin(p * math.pi * 2.0) * (1 - p)
        return off, 1 - s * 0.8, 1 + s, 1.0
    off = 6 * math.sin(2 * math.pi * 0.7 * (t - 1.9)) * -1
    sx = sy = 1.0
    if 12.9 <= t < 13.3:
        hp = abs(math.sin(math.pi * (t - 12.9) / 0.2))
        off -= 55 * hp
        sy = 1 + 0.06 * hp
        sx = 1 - 0.05 * hp
    sc = 1.0
    if t >= 14.0:
        sc = 1 - sstep((t - 14.0) / 0.35)
        if sc <= 0.01:
            return None
    return off, sx, sy, sc


def star(d, cx, cy, r, color):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append(((cx + rr * math.cos(ang)) * S, (cy + rr * math.sin(ang)) * S))
    d.polygon(pts, fill=color)


_bg = None


def background():
    global _bg
    if _bg is not None:
        return _bg.copy()
    im = Image.new('RGB', (W * S, H * S))
    d = ImageDraw.Draw(im)
    for y in range(H * S):
        c = mix((234, 240, 250), (212, 222, 239), y / (H * S))
        d.line([(0, y), (W * S, y)], fill=c)
    # taskbar
    d.rectangle([0, 690 * S, W * S, H * S], fill=(30, 41, 59))
    for i, col in enumerate([(91, 141, 239), (125, 249, 255), (255, 209, 102), (249, 168, 212)]):
        d.rounded_rectangle([(24 + i * 44) * S, 697 * S, (24 + i * 44 + 30) * S, 713 * S], radius=5 * S, fill=col)
    # doc window
    d.rounded_rectangle([54 * S, 56 * S, 744 * S, 676 * S], radius=14 * S, fill=(196, 206, 223))
    d.rounded_rectangle([50 * S, 50 * S, 740 * S, 670 * S], radius=14 * S, fill=(255, 255, 255),
                        outline=(184, 196, 214), width=2 * S)
    d.rounded_rectangle([50 * S, 50 * S, 740 * S, 96 * S], radius=14 * S, fill=(232, 237, 245))
    d.rectangle([51 * S, 80 * S, 739 * S, 96 * S], fill=(232, 237, 245))
    for i, col in enumerate([(248, 113, 113), (251, 191, 36), (74, 222, 128)]):
        d.ellipse([(72 + i * 24) * S, 66 * S, (86 + i * 24) * S, 80 * S], fill=col)
    d.text((300 * S, 62 * S), "Report.doc", font=font(18), fill=(100, 116, 139))
    d.line([(50 * S, 96 * S), (740 * S, 96 * S)], fill=(210, 218, 232), width=2 * S)
    _bg = im
    return im.copy()


def draw_doc(d, t):
    total = sum(len(l) for l in BODY_TEXT)
    n = int(clamp(t / 1.0) * total)
    y = 190
    typed_end = (90, y)
    for line in BODY_TEXT:
        k = min(len(line), n)
        if k > 0:
            d.text((90 * S, y * S), line[:k], font=font(22), fill=(55, 65, 81))
            typed_end = (90 + font(22).getlength(line[:k]) / S, y)
        n -= k
        y += 38
        if n <= 0:
            break
    # title typed by the bulb idea
    if t >= 8.2:
        title = "Quarterly Report"
        k = int(clamp((t - 8.2) / 0.8) * len(title))
        d.text((90 * S, 120 * S), title[:k], font=font(36, True), fill=(17, 24, 39))
        if k == len(title):
            d.rounded_rectangle([90 * S, 168 * S, (90 + 120) * S, 173 * S], radius=2 * S, fill=BODY)
    if t < 8.2 or t > 9.4:
        pass
    if int(t * 2) % 2 == 0 and t < 8.2:
        cx, cy = typed_end
        d.rectangle([(cx + 3) * S, (cy + 1) * S, (cx + 5) * S, (cy + 28) * S], fill=BODY)
    # tap ripples
    for tt in TAP_TIMES:
        dt = t - tt
        if 0 <= dt < 0.45:
            p = dt / 0.45
            r = 8 + 46 * p
            col = mix(BODY, (255, 255, 255), p)
            d.ellipse([(742 - r) * S, (318 - r) * S, (742 + r) * S, (318 + r) * S], outline=col, width=3 * S)
    # sparkle when the title lands
    if 8.7 <= t < 9.2:
        p = (t - 8.7) / 0.5
        star(d, 330, 130, 10 + 8 * math.sin(p * math.pi), YEL)
        star(d, 350, 160, 6 + 5 * math.sin(p * math.pi), BODY)


def draw_byte(d, t):
    st = byte_vert(t)
    if st is None:
        return None
    off, sx, sy, sc = st
    bx = byte_x(t)
    base = 618 + off
    sx *= sc
    sy *= sc
    # shadow
    height = max(0, -off)
    sw = 110 * sx * (1 - 0.003 * min(height, 60))
    if off < 200:
        d.ellipse([(bx - sw) * S, 650 * S, (bx + sw) * S, 666 * S], fill=(196, 206, 223))

    def P(x, y):
        return ((bx + x * K * sx) * S, (base + y * K * sy) * S)

    def R(x0, y0, x1, y1):
        a = P(x0, y0)
        b = P(x1, y1)
        return [a[0], a[1], b[0], b[1]]

    kk = K * (sx + sy) / 2 * S
    sadf = sstep((t - 11.7) / 0.3) - sstep((t - 12.7) / 0.3)
    glow = 0.0
    if 7.3 <= t < 9.4:
        glow = sstep((t - 7.3) / 0.15) * (0.75 + 0.25 * math.sin((t - 7.3) * 9))
    tipx = 6 * math.sin(2 * math.pi * 1.1 * t) * (3 if 5.5 <= t < 7.0 else 1)
    tipx = lerp(tipx, 18, sadf)
    tipy = lerp(-165, -146, sadf)
    # antenna
    d.line([P(0, -126), P(tipx, tipy)], fill=BODY_D, width=int(5 * kk))
    tc = P(tipx, tipy)
    if glow > 0:
        for r, a in ((26, 0.25), (18, 0.45)):
            c = mix((255, 255, 255), YEL, 0.4 + 0.6 * a)
            rr = r * (0.5 + 0.5 * glow) * kk
            d.ellipse([tc[0] - rr, tc[1] - rr, tc[0] + rr, tc[1] + rr], fill=mix((255, 255, 255), YEL, 0.35 * glow + 0.1))
    rr = 9 * kk
    d.ellipse([tc[0] - rr, tc[1] - rr, tc[0] + rr, tc[1] + rr], fill=mix((239, 68, 68), YEL, glow), outline=BODY_D, width=int(2 * S))
    # body
    d.rounded_rectangle(R(-75, -130, 75, 0), radius=int(38 * kk), fill=BODY, outline=BODY_D, width=int(4 * S))
    d.polygon([P(-58, -8), P(-64, 26), P(-18, -6), P(-18, -8)], fill=BODY)
    d.line([P(-58, -4), P(-64, 26), P(-20, -4)], fill=BODY_D, width=int(4 * S))
    d.line([P(-52, -122), P(-30, -126)], fill=(160, 190, 250), width=int(5 * kk / 1.6))
    # face plate
    d.rounded_rectangle(R(-58, -114, 58, -36), radius=int(24 * kk), fill=PLATE)
    lx, ly = keyinterp(LOOK, t)
    m = mood(t)
    b = blink(t)
    for ex in (-26, 26):
        cx = ex + 8 * lx
        cy = -76 + 6 * ly
        if m == 'happy':
            d.arc(R(cx - 15, cy - 10, cx + 15, cy + 20), 200, 340, fill=EYE, width=int(6 * kk / 1.6))
        else:
            hh = 32 * (1 - 0.95 * b) * (0.72 if m == 'sad' else 1)
            d.rounded_rectangle(R(cx - 11, cy - hh / 2, cx + 11, cy + hh / 2), radius=int(10 * kk), fill=EYE)
            if m == 'sad':
                if ex < 0:
                    d.line([P(cx - 13, cy - 24), P(cx + 11, cy - 36)], fill=EYE, width=int(4 * kk / 1.6))
                else:
                    d.line([P(cx - 11, cy - 36), P(cx + 13, cy - 24)], fill=EYE, width=int(4 * kk / 1.6))
    for ex in (-46, 46):
        d.ellipse(R(ex - 8, -56, ex + 8, -46), fill=CHEEK)
    # tear when sad
    if 11.8 <= t < 12.5:
        p = (t - 11.8) / 0.7
        tx, ty = P(-34, -62 + 28 * p)
        r = 4 * kk
        d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(125, 200, 255))
    # mouth
    if m == 'sad':
        d.arc(R(-10, -50, 10, -34), 200, 340, fill=EYE, width=int(4 * kk / 1.6))
    elif talking(t):
        mh = 4 + 9 * abs(math.sin(t * 14))
        d.rounded_rectangle(R(-8, -52, 8, -52 + mh), radius=int(5 * kk), fill=EYE)
    elif m == 'happy':
        d.pieslice(R(-12, -58, 12, -38), 0, 180, fill=EYE)
    else:
        d.arc(R(-10, -58, 10, -42), 20, 160, fill=EYE, width=int(4 * kk / 1.6))
    # arms
    hl = keyinterp(HAND_L, t, 0.3)
    hr = keyinterp(HAND_R, t, 0.3)
    hl = list(hl)
    hr = list(hr)
    if 5.55 <= t < 6.95:
        hl[0] = -100 - 12 * (1 - abs(math.sin(math.pi * (t - 5.6) / 0.4)))
        hl[1] = -62
    if t >= 13.5:
        hr[0] += 14 * math.sin(2 * math.pi * 3 * (t - 13.5))
    for (sxp, hand) in ((-72, hl), (72, hr)):
        d.line([P(sxp, -58), P(hand[0], hand[1])], fill=ARM, width=int(10 * kk / 1.6 * 1.0))
        hp = P(hand[0], hand[1])
        r = 12 * kk
        d.ellipse([hp[0] - r, hp[1] - r, hp[0] + r, hp[1] + r], fill=ARM, outline=BODY_D, width=int(2 * S))
    props = dict(bx=bx, base=base, hr=P(hr[0], hr[1]), tip=tc, sc=sc)
    return props


def draw_bulb(d, props, t):
    if not (7.3 <= t < 9.4):
        return
    s = back((t - 7.3) / 0.35)
    cx, cy = props['bx'] + 100, 338 - 6 * math.sin((t - 7.3) * 4)
    rr = 24 * s
    pulse = 0.6 + 0.4 * math.sin((t - 7.3) * 9)
    for i in range(8):
        a = i * math.pi / 4 + 0.2
        r0, r1 = (34 + 4 * pulse) * s, (48 + 8 * pulse) * s
        d.line([((cx + r0 * math.cos(a)) * S, (cy + r0 * math.sin(a)) * S),
                ((cx + r1 * math.cos(a)) * S, (cy + r1 * math.sin(a)) * S)], fill=YEL, width=4 * S)
    d.ellipse([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], fill=YEL, outline=(217, 160, 40), width=2 * S)
    d.rounded_rectangle([(cx - 10 * s) * S, (cy + rr - 4) * S, (cx + 10 * s) * S, (cy + rr + 12 * s) * S], radius=3 * S, fill=(148, 163, 184))
    d.arc([(cx - 12 * s) * S, (cy - 12 * s) * S, (cx + 4 * s) * S, (cy + 4 * s) * S], 200, 280, fill=(255, 245, 200), width=3 * S)


def draw_envelope(d, props, t):
    if not (9.6 <= t < 12.5):
        return
    hx, hy = props['hr'][0] / S, props['hr'][1] / S
    ex, ey = hx, hy - 36 + 3 * math.sin(t * 5)
    if t >= 11.5:
        fall = t - 11.5
        ey += 500 * fall * fall
        ex += 30 * fall
    s = back((t - 9.6) / 0.3) if t < 11.5 else 1
    w, h = 64 * s, 44 * s
    d.rounded_rectangle([(ex - w / 2) * S, (ey - h / 2) * S, (ex + w / 2) * S, (ey + h / 2) * S], radius=5 * S,
                        fill=(255, 255, 255), outline=(100, 116, 139), width=2 * S)
    d.line([((ex - w / 2) * S, (ey - h / 2) * S), (ex * S, (ey + h * 0.1) * S), ((ex + w / 2) * S, (ey - h / 2) * S)],
           fill=(100, 116, 139), width=2 * S)


def draw_bubble(d, props, t):
    seg = None
    for s, e, txt in BUBBLES:
        if s <= t < e:
            seg = (s, e, txt)
    if seg is None or props is None:
        return
    s0, e0, txt = seg
    bx = props['bx']
    lines = txt.split('\n')
    f = font(26)
    tw = max(f.getlength(l) for l in lines) / S
    w, h = tw + 56, len(lines) * 38 + 30
    cx = clamp(bx + 20, 790 + w / 2, 1250 - w / 2)
    x0, x1 = cx - w / 2, cx + w / 2
    y1 = 262
    y0 = y1 - h
    tipx, tipy = bx - 36, 336
    sc = back((t - s0) / 0.2)
    if t > e0 - 0.12:
        sc *= clamp((e0 - t) / 0.12)

    def T(x, y):
        return ((tipx + (x - tipx) * sc) * S, (tipy + (y - tipy) * sc) * S)

    tbx = clamp(tipx - 22, x0 + 22, x1 - 62)
    # shadow, bubble, tail
    a, b = T(x0 + 3, y0 + 5), T(x1 + 3, y1 + 5)
    d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(22 * S * sc), fill=(196, 206, 223))
    a, b = T(x0, y0), T(x1, y1)
    d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(22 * S * sc), fill=(255, 255, 255), outline=(184, 196, 214), width=2 * S)
    tail = [T(tbx, y1 - 4), T(tbx + 38, y1 - 4), T(tipx, tipy)]
    d.polygon(tail, fill=(255, 255, 255))
    d.line([T(tbx, y1 - 1), T(tipx, tipy), T(tbx + 38, y1 - 1)], fill=(184, 196, 214), width=2 * S)
    d.line([T(tbx + 3, y1 - 2), T(tbx + 35, y1 - 2)], fill=(255, 255, 255), width=4 * S)
    if sc > 0.97:
        n = int((t - s0 - 0.2) * CPS)
        yy = y0 + 15
        for l in lines:
            k = max(0, min(len(l), n))
            if k > 0:
                d.text(((x0 + 28) * S, yy * S), l[:k], font=f, fill=INK)
            n -= len(l)
            yy += 38
        # typing dots while "thinking" at the start of bubble 2
    return


def draw_poof(d, props_x, t):
    if 14.0 <= t < 14.7:
        p = (t - 14.0) / 0.7
        cx, cy = 1020, 520
        for i in range(8):
            a = i * math.pi / 4 + 0.3
            r = 40 + 110 * p
            col = [YEL, BODY, CHEEK, EYE][i % 4]
            star(d, cx + r * math.cos(a), cy + r * math.sin(a) * 0.8, 14 * (1 - p) + 3, col)


def frame(t):
    im = background()
    d = ImageDraw.Draw(im)
    draw_doc(d, t)
    props = draw_byte(d, t)
    draw_bulb(d, props or {'bx': 1020}, t)
    if props:
        draw_envelope(d, props, t)
    draw_bubble(d, props, t)
    draw_poof(d, None, t)
    return im.resize((W, H), Image.LANCZOS)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preview':
        times = [float(x) for x in sys.argv[2:]]
        sheet = Image.new('RGB', (W, H * len(times) // 2 if False else H * ((len(times) + 1) // 2)), (0, 0, 0))
        for i, tt in enumerate(times):
            fr = frame(tt)
            fr.save(os.path.join(HERE, f'prev_{i}.png'))
    else:
        out = os.path.join(HERE, 'byte_helper_clip.mp4')
        tmp = os.path.join(HERE, 'byte_helper_clip.part.mp4')
        cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
               '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(DUR * FPS)
        for i in range(n):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        rc = p.wait()
        if rc == 0:
            os.rename(tmp, out)
            print('done', out)
        else:
            print('ffmpeg failed', rc)
            sys.exit(rc)
