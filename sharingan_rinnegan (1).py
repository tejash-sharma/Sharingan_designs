"""
Eternal Mangekyo Sharingan (left, pattern rotates clockwise)
and Rinnegan (right, shape static, colour drifts lavender <-> light purple) drawn with Python turtle.

All coordinates below were measured from the reference image (1672 x 941 px)
and converted to turtle coordinates by tx() / ty().
Run:  python sharingan_rinnegan.py
"""
import math
import turtle

# --------------------------------------------------------------------------
# Window / coordinate mapping (reference image = 1672 x 941)
# --------------------------------------------------------------------------
IMG_W, IMG_H = 1672, 941
SCALE = 0.75                                  # shrink so it fits on any screen
WIN_W, WIN_H = int(IMG_W * SCALE), int(IMG_H * SCALE)


def tx(x):                                    # image-px -> turtle x
    return (x - IMG_W / 2) * SCALE


def ty(y):                                    # image-px -> turtle y (y flipped)
    return (IMG_H / 2 - y) * SCALE


# --------------------------------------------------------------------------
# Colours (sampled from the reference)
# --------------------------------------------------------------------------
BLACK = "#000000"
WHITE = "#f4f4f4"
RED = "#cf0a0a"

# --------------------------------------------------------------------------
# Screen
# --------------------------------------------------------------------------
screen = turtle.Screen()
screen.setup(WIN_W, WIN_H)
screen.bgcolor(BLACK)
screen.title("Rotating Mangekyo Sharingan  &  Static Rinnegan")
screen.tracer(0)                              # manual refresh = smooth animation

static_pen = turtle.Turtle(visible=False)     # left eye base, drawn once
spin_pen = turtle.Turtle(visible=False)       # rotating pattern, redrawn each frame
right_pen = turtle.Turtle(visible=False)      # Rinnegan, redrawn when its colour changes
for p in (static_pen, spin_pen, right_pen):
    p.hideturtle()
    p.speed(0)
    p.penup()


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def catmull_rom(pts, n=14):
    """Smooth curve through pts (open ends keep their sharp tips)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(pts[-1])
    return out


def inside(poly, x, y):
    """Ray-casting point-in-polygon test."""
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def fill_poly(t, pts, fill, outline=None, width=1):
    """pts are already in turtle coordinates."""
    t.color(outline or fill, fill)
    t.pensize(width)
    t.penup()
    t.goto(pts[0])
    t.pendown()
    t.begin_fill()
    for p in pts[1:]:
        t.goto(p)
    t.goto(pts[0])
    t.end_fill()
    t.penup()


def circle_pts(cx, cy, rx, ry=None, n=90):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(2 * math.pi * i / n),
             cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def to_turtle(pts):
    return [(tx(x), ty(y)) for x, y in pts]


# --------------------------------------------------------------------------
# LEFT EYE  -  white sclera + black iris (static)
# --------------------------------------------------------------------------
L_TOP = [(45, 370), (130, 335), (250, 312), (380, 303), (480, 318),
         (580, 375), (670, 460), (730, 535), (762, 578)]
L_BOT = [(762, 578), (700, 592), (600, 610), (500, 620), (420, 622),
         (330, 612), (240, 580), (150, 510), (90, 440), (45, 370)]
left_outline = catmull_rom(L_TOP) + catmull_rom(L_BOT)

IRIS_C = (388, 463)                           # iris centre (image px)
IRIS_R = 162

fill_poly(static_pen, to_turtle(left_outline), WHITE)
fill_poly(static_pen, to_turtle(circle_pts(*IRIS_C, IRIS_R, n=120)), BLACK)

# --------------------------------------------------------------------------
# RIGHT EYE  -  Rinnegan.  Shape/rings/tomoe never move; only the purple
# fill colour drifts between LAVENDER and LIGHT PURPLE.
# --------------------------------------------------------------------------
LAVENDER = (176, 158, 230)
LIGHT_PURPLE = (216, 170, 242)


def rinnegan_color(phase):
    """phase in radians; smooth loop lavender -> light purple -> lavender."""
    m = (1 - math.cos(phase)) / 2
    r, g, b = (round(a + (c - a) * m) for a, c in zip(LAVENDER, LIGHT_PURPLE))
    return "#%02x%02x%02x" % (r, g, b)


R_TOP = [(897, 578), (940, 520), (1000, 450), (1070, 395), (1150, 350),
         (1230, 325), (1300, 318), (1380, 320), (1470, 335), (1550, 358),
         (1616, 378)]
R_BOT = [(1616, 378), (1585, 440), (1540, 500), (1480, 555), (1410, 600),
         (1330, 623), (1260, 628), (1180, 622), (1090, 607), (990, 590),
         (897, 578)]
right_outline = catmull_rom(R_TOP) + catmull_rom(R_BOT)
right_outline_t = to_turtle(right_outline)

RC = (1279.5, 471)                            # common centre of pupil + all rings
PUPIL = RC


def clipped_segments(pts, clip):
    """Split a polyline into pieces that lie inside the eye shape."""
    segs, cur = [], []
    for (x, y) in pts:
        if inside(clip, x, y):
            cur.append((tx(x), ty(y)))
        elif cur:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


# concentric rings: (radius, line width in turtle px).  The first two are the
# rings that carry the tomoe; the rest are the big rings clipped by the eye.
ring_segments = []                            # list of (segment, width)
RING_SPEC = [(72, 2.4), (118, 2.9)] + [(r, 3.7) for r in (163, 208, 253, 298, 343, 388)]
for k, (rx, wdt) in enumerate(RING_SPEC):
    ry = rx * (1.0 if k < 2 else 1.0 + 0.045 * (k - 1))   # outer rings get taller
    pts = circle_pts(RC[0], RC[1], rx, ry, n=420)
    pts.append(pts[0])
    for seg in clipped_segments(pts, right_outline):
        ring_segments.append((seg, wdt))

# six tomoe: centre (image px) + tail (start deg, end deg) swept round the head.
# Angles are screen angles (y down, so + is clockwise).  Measured from the reference.
TR = 17.5
TOMOE = [
    ((1277.5, 398.0), -150, -48),     # top          (inner ring)
    ((1370.5, 407.5), -108, 8),       # upper right  (outer ring)
    ((1346.0, 502.5), -18, 80),       # lower right  (inner ring)
    ((1283.8, 584.0), 25, 132),       # bottom       (outer ring)
    ((1218.8, 507.5), 95, 192),       # lower left   (inner ring)
    ((1188.8, 410.0), 260, 172),      # upper left   (mirrored hook, see reference)
]


def tail_poly(c, a0, a1, w0=8.0, reach=0.85, n=22, p=1.2):
    """Thin crescent tail hugging the head, tapering to a needle point."""
    pts_out, pts_in = [], []
    for i in range(n + 1):
        u = i / n
        phi = math.radians(a0 + (a1 - a0) * u)
        r_in = TR * (0.9 + reach * u ** p)
        r_out = r_in + w0 * (1 - u) ** 0.8
        pts_in.append((c[0] + r_in * math.cos(phi), c[1] + r_in * math.sin(phi)))
        pts_out.append((c[0] + r_out * math.cos(phi), c[1] + r_out * math.sin(phi)))
    return to_turtle(pts_out + pts_in[::-1])


tomoe_polys = []
for (c, a0, a1) in TOMOE:
    tomoe_polys.append(to_turtle(circle_pts(c[0], c[1], TR, n=48)))
    tomoe_polys.append(tail_poly(c, a0, a1))
# tiny extra spike under the upper-left tomoe (present in the reference)
tomoe_polys.append(tail_poly((1188.8, 410.0), 62, 84, w0=4.5, reach=0.55, p=1.0))

pupil_poly = to_turtle(circle_pts(PUPIL[0], PUPIL[1], 24, n=60))


def stroke(t, seg):
    t.penup()
    t.goto(seg[0])
    t.pendown()
    for p in seg[1:]:
        t.goto(p)
    t.penup()


def draw_rinnegan(col):
    t = right_pen
    t.clear()
    fill_poly(t, right_outline_t, col)
    t.color(BLACK)
    for seg, wdt in ring_segments:
        t.pensize(wdt)
        stroke(t, seg)
    for poly in tomoe_polys:
        fill_poly(t, poly, BLACK)
    fill_poly(t, pupil_poly, BLACK)


# --------------------------------------------------------------------------
# ROTATING PATTERN  (Eternal Mangekyo Sharingan, inside the black iris)
# --------------------------------------------------------------------------
def petal(angle_deg, tip=150, half=44, n=24):
    """Pointed lens-shaped petal from the centre outwards (image px)."""
    a = math.radians(angle_deg)
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        r = t * tip
        w = half * math.sin(math.pi * t ** 0.85)
        left.append((r, w))
        right.append((r, -w))
    pts = left + right[::-1]
    return [(IRIS_C[0] + r * math.cos(a) - w * math.sin(a),
             IRIS_C[1] - (r * math.sin(a) + w * math.cos(a))) for r, w in pts]


def polar(r, deg, spin):
    a = math.radians(deg) + spin
    return (IRIS_C[0] + r * math.cos(a), IRIS_C[1] - r * math.sin(a))


def bezier(p0, c, p2, n=18):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * c[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * c[1] + u * u * p2[1])
            for u in (i / n for i in range(n + 1))]


# three needle tips: (angle, radius) - two arms up-left / up-right, long blade down
SHURIKEN_TIPS = [(154, 126), (26, 126), (270, 138)]


BLADE_WIDTH = 12                              # bigger = fatter blades (control-point push)


def shuriken(spin):
    """Curved three-pointed shuriken: concave sides, wide in the middle, needle tips."""
    tips = [(polar(r, a, spin), a) for a, r in SHURIKEN_TIPS]
    poly = []
    for i in range(3):
        (p0, a0), (p1, a1) = tips[i], tips[(i + 1) % 3]
        # push direction = bisector of the two neighbouring tips (rotates with spin)
        vx, vy = p0[0] + p1[0] - 2 * IRIS_C[0], p0[1] + p1[1] - 2 * IRIS_C[1]
        d = math.hypot(vx, vy) or 1
        c = (IRIS_C[0] + BLADE_WIDTH * vx / d, IRIS_C[1] + BLADE_WIDTH * vy / d)
        poly += bezier(p0, c, p1)[:-1]
    return poly


def draw_pattern(spin):
    """spin = rotation in radians (negative = clockwise)."""
    t = spin_pen
    t.clear()

    # six red petals
    for k in range(6):
        fill_poly(t, to_turtle(petal(90 + 60 * k + math.degrees(spin))), RED)

    t.color(BLACK)
    # bold black rosette: six big circles (R=171, centres 114 px out, 60 deg apart),
    # only the part inside radius 90 is drawn - exactly the arcs seen in the reference
    t.color(BLACK)
    t.pensize(3)
    for k in range(6):
        cx, cy = polar(114, 60 * k, spin)
        pts = [(cx + 171 * math.cos(2 * math.pi * i / 360),
                cy + 171 * math.sin(2 * math.pi * i / 360)) for i in range(361)]
        seg = []
        for (x, y) in pts:
            if math.hypot(x - IRIS_C[0], y - IRIS_C[1]) <= 90:
                seg.append((tx(x), ty(y)))
            elif seg:
                stroke(t, seg)
                seg = []
        if seg:
            stroke(t, seg)

    # black three-pointed shuriken
    fill_poly(t, to_turtle(shuriken(spin)), BLACK)

    # black ring + big red dot in the centre
    fill_poly(t, to_turtle(circle_pts(*IRIS_C, 27, n=60)), BLACK)
    fill_poly(t, to_turtle(circle_pts(*IRIS_C, 19, n=60)), RED)


# --------------------------------------------------------------------------
# Animation loop
#   left  : pattern spins clockwise
#   right : same shape, colour drifts lavender <-> light purple
# --------------------------------------------------------------------------
angle = 0.0
phase = 0.0
STEP = math.radians(2.5)                      # degrees per frame
COLOR_STEP = 2 * math.pi / 240                # one colour cycle = 240 frames
FRAME_MS = 16
frame = 0


def animate():
    global angle, phase, frame
    frame += 1
    angle -= STEP                             # minus = clockwise
    draw_pattern(angle)
    if frame % 2 == 0:                        # recolour every 2nd frame (cheaper)
        phase += COLOR_STEP * 2
        draw_rinnegan(rinnegan_color(phase))
    screen.update()
    screen.ontimer(animate, FRAME_MS)


draw_pattern(0)
draw_rinnegan(rinnegan_color(0))
screen.update()

if __name__ == "__main__":
    animate()
    screen.mainloop()
