import math


L1x = 70 # x offset relative to the center of rotation (mm)
L1z = 78 # z offset relative to the center of rotation (mm)
L2 = 145.1 # length of the first part (mm)
L3 = 177 # length of the second part (mm)
L4 = 38.1 # length of the tool (mm) unused

def ik(x, y, z, r):
    # angle of the base
    t0 = math.atan2(y, x)

    d = math.sqrt((x - L1x * math.cos(t0)) ** 2 + (z - L1z) ** 2 + (y - L1x * math.sin(t0)) ** 2)
    dx = math.sqrt(d**2 - (z - L1z)**2)

    A1 = math.atan2(z - L1z, dx)

    A2 = coslaw(d, L2, L3)

    t1 = A1 + A2

    t2 = coslaw(L2, L3, d)

    t3 = t1 + t2 + - r - math.pi # + maybe offset?

    return [t0, t1, t2, t3]


def coslaw(a, b, c):
    return math.acos((a ** 2 + b ** 2 - c ** 2) / (2 * a * b))
