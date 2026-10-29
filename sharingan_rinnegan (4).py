"""
Eternal Mangekyo Sharingan (left, pattern rotates clockwise)
and Rinnegan (right, static) drawn with Python turtle.

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
PURPLE = "#8f77ab"

# --------------------------------------------------------------------------
# Screen
# --------------------------------------------------------------------------
screen = turtle.Screen()
screen.setup(WIN_W, WIN_H)
screen.bgcolor(BLACK)
screen.title("Rotating Mangekyo Sharingan  &  Static Rinnegan")
screen.tracer(0)                              # manual refresh = smooth animation

static_pen = turtle.Turtle(visible=False)     # drawn once
spin_pen = turtle.Turtle(visible=False)       # redrawn every frame
for p in (static_pen, spin_pen):
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
# RIGHT EYE  -  purple Rinnegan (static)
# --------------------------------------------------------------------------
R_TOP = [(897, 578), (940, 520), (1000, 450), (1070, 395), (1150, 350),
         (1230, 325), (1300, 318), (1380, 320), (1470, 335), (1550, 358),
         (1616, 378)]
R_BOT = [(1616, 378), (1585, 440), (1540, 500), (1480, 555), (1410, 600),
         (1330, 623), (1260, 628), (1180, 622), (1090, 607), (990, 590),
         (897, 578)]
right_outline = catmull_rom(R_TOP) + catmull_rom(R_BOT)
fill_poly(static_pen, to_turtle(right_outline), PURPLE)

RC = (1280, 478)                              # centre of the concentric rings

def draw_clipped(pts, clip):
    """Draw a polyline, lifting the pen wherever it leaves the eye shape."""
    pen_down = False
    for (x, y) in pts:
        if inside(clip, x, y):
            static_pen.goto(tx(x), ty(y))
            if not pen_down:
                static_pen.pendown()
                pen_down = True
        else:
            static_pen.penup()
            pen_down = False
    static_pen.penup()

# bold concentric rings (clipped to the eye shape, run right up to its edge)
static_pen.color(BLACK)
static_pen.pensize(6 * SCALE)
ring_radii = [128, 170, 214, 258, 302, 346, 390]
for k, rx in enumerate(ring_radii):
    ry = rx * (1.0 + 0.05 * k)
    pts = circle_pts(RC[0], RC[1], rx, ry, n=900)
    pts.append(pts[0])
    draw_clipped(pts, right_outline)

# thin ring that carries the six tomoe
static_pen.pensize(3 * SCALE)
pts = circle_pts(1280, 490, 93, 93, n=240)
pts.append(pts[0])
draw_clipped(pts, right_outline)

# six tomoe (black dot + curved tail) - centres measured from the image
TOMOE = [(1277, 397), (1368, 408), (1344, 507),
         (1282, 583), (1218, 507), (1190, 410)]
TR = 17
for (x, y) in TOMOE:
    fill_poly(static_pen, to_turtle(circle_pts(x, y, TR, n=40)), BLACK)
    # curved tail, sweeping clockwise round the ring centre, tapering to a point
    r0 = math.hypot(x - 1280, y - 490)
    ang = math.atan2(y - 490, x - 1280)       # image y is down -> +angle = clockwise
    outer, inner = [], []
    N = 16
    for i in range(N + 1):
        u = i / N
        a_c = ang + 0.10 + 0.34 * u
        rc = r0 + TR * 0.55 * (1 - u) ** 0.9
        w = TR * 0.95 * (1 - u) ** 0.85
        outer.append((1280 + (rc + w / 2) * math.cos(a_c), 490 + (rc + w / 2) * math.sin(a_c)))
        inner.append((1280 + (rc - w / 2) * math.cos(a_c), 490 + (rc - w / 2) * math.sin(a_c)))
    fill_poly(static_pen, to_turtle(outer + inner[::-1]), BLACK)

# centre pupil (plain black dot)
fill_poly(static_pen, to_turtle(circle_pts(1280, 468, 27, n=60)), BLACK)

# --------------------------------------------------------------------------
# ROTATING PATTERN  (Eternal Mangekyo Sharingan, inside the black iris)
# --------------------------------------------------------------------------
def rot(px, py, a):
    """Rotate local point (px,py) by angle a (radians, CCW) -> image px."""
    c, s = math.cos(a), math.sin(a)
    return (IRIS_C[0] + px * c - py * s, IRIS_C[1] - (px * s + py * c))


def petal(angle_deg, tip=150, half=44, n=24):
    """Pointed lens-shaped red petal from the centre outwards."""
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


def draw_pattern(spin):
    """spin = rotation in radians (negative = clockwise)."""
    t = spin_pen
    t.clear()

    # six red petals
    for k in range(6):
        pts = petal(90 + 60 * k + math.degrees(spin))
        fill_poly(t, to_turtle(pts), RED)

    # thin black lens outline inside each red petal
    t.color(BLACK)
    t.pensize(2)
    for k in range(6):
        pts = petal(90 + 60 * k + math.degrees(spin), tip=142, half=38)
        t.penup()
        t.goto(tx(pts[0][0]), ty(pts[0][1]))
        t.pendown()
        for (x, y) in pts[1:] + [pts[0]]:
            t.goto(tx(x), ty(y))
        t.penup()

    # thin black overlapping circle lines
    t.color(BLACK)
    t.pensize(2)
    for k in range(3):
        base = 90 + 120 * k
        cx, cy = polar(62, base, spin)
        pts = circle_pts(cx, cy, 98, n=90)
        pts.append(pts[0])
        t.penup()
        t.goto(tx(pts[0][0]), ty(pts[0][1]))
        t.pendown()
        for (x, y) in pts[1:]:
            t.goto(tx(x), ty(y))
        t.penup()

    # black three-pronged shuriken shape (prongs at 30, 150, 270 deg)
    # dagger profile: (radius along blade, half-width) - widest mid-blade
    DAGGER = [(42, 13), (66, 21), (90, 23), (112, 14), (134, 0)]

    def blade_pt(a_deg, r, w):
        a = math.radians(a_deg) + spin
        return (IRIS_C[0] + r * math.cos(a) - w * math.sin(a),
                IRIS_C[1] - (r * math.sin(a) + w * math.cos(a)))

    poly = []
    for a in (30, 150, 270):
        poly.append(polar(34, a - 60, spin))                   # valley between blades
        poly += [blade_pt(a, r, -w) for r, w in DAGGER]        # one side up to the tip
        poly += [blade_pt(a, r, w) for r, w in DAGGER[-2::-1]] # other side back down
    fill_poly(t, to_turtle(poly), BLACK)

    # black ring + red dot in the centre
    fill_poly(t, to_turtle(circle_pts(*IRIS_C, 38, n=60)), BLACK)
    fill_poly(t, to_turtle(circle_pts(*IRIS_C, 27, n=60)), RED)


# --------------------------------------------------------------------------
# Animation loop  (clockwise rotation, right eye never changes)
# --------------------------------------------------------------------------
angle = 0.0
STEP = math.radians(2.5)                      # degrees per frame
FRAME_MS = 16


def animate():
    global angle
    angle -= STEP                             # minus = clockwise
    draw_pattern(angle)
    screen.update()
    screen.ontimer(animate, FRAME_MS)


draw_pattern(0)
screen.update()

if __name__ == "__main__":
    animate()
    screen.mainloop()
