"""
Apollonian Gasket — recursive fractal animation.

Run this file; a window opens and the gasket reveals itself one generation
at a time. Tweak the parameters at the top to play.

The math: Descartes' Circle Theorem. For four mutually tangent circles with
curvatures (k = 1/radius, negative if the circle contains the others):

    (k1 + k2 + k3 + k4)^2 = 2 * (k1^2 + k2^2 + k3^2 + k4^2)

Given any three mutually tangent circles, two circles are tangent to all
three (one on each side of the curvy triangle they form). Apply recursively.

Requires: numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

# ── Parameters to play with ───────────────────────────────────────────
INITIAL_K = (2.0, 2.0, 3.0)   # curvatures of the three starting inner
                              # circles. Equal values => symmetric gasket.
                              # Try (2, 2, 2), (1, 2, 3), (2, 3, 5)...
MAX_DEPTH = 7                 # how many generations to compute.
                              # Higher = more detail, more compute.
MIN_RADIUS = 0.003            # stop recursing when circles shrink below this.
REVEAL_INTERVAL_MS = 400      # ms between generations during animation.
COLORMAP = "twilight"         # try: plasma, viridis, magma, inferno, cividis
LINE_WIDTH = 0.9
BG_COLOR = "#0a0a0a"
FIG_SIZE = 8                  # inches, square
# ──────────────────────────────────────────────────────────────────────


def fourth_circle(k1, k2, k3, z1, z2, z3, k_prev, z_prev):
    """
    Given three mutually tangent circles (k1/z1, k2/z2, k3/z3) and one of
    the two circles tangent to all three (k_prev/z_prev), return the OTHER
    tangent circle via Vieta's formula — more numerically stable than
    re-solving from scratch.
    """
    sum_k = k1 + k2 + k3
    sum_kz = k1 * z1 + k2 * z2 + k3 * z3
    k_new = 2 * sum_k - k_prev
    z_new = (2 * sum_kz - k_prev * z_prev) / k_new
    return k_new, z_new


def both_fourth_circles(k1, k2, k3, z1, z2, z3):
    """Both circles tangent to the three given ones (no prior known)."""
    sum_k = k1 + k2 + k3
    disc = max(k1 * k2 + k2 * k3 + k3 * k1, 0.0)
    sqrt_k = np.sqrt(disc)
    k_plus = sum_k + 2 * sqrt_k
    k_minus = sum_k - 2 * sqrt_k

    sum_kz = k1 * z1 + k2 * z2 + k3 * z3
    disc_z = k1 * k2 * z1 * z2 + k2 * k3 * z2 * z3 + k3 * k1 * z3 * z1
    sqrt_z = np.sqrt(disc_z + 0j)
    z_plus = (sum_kz + 2 * sqrt_z) / k_plus if k_plus != 0 else 0j
    z_minus = (sum_kz - 2 * sqrt_z) / k_minus if k_minus != 0 else 0j
    return (k_plus, z_plus), (k_minus, z_minus)


def initial_configuration(k1, k2, k3):
    """Place three mutually tangent inner circles + the enclosing outer."""
    r1, r2, r3 = 1 / k1, 1 / k2, 1 / k3
    # Place z1 at origin, z2 on the real axis, then triangulate z3.
    z1 = 0 + 0j
    z2 = (r1 + r2) + 0j
    d13 = r1 + r3
    d23 = r2 + r3
    d12 = r1 + r2
    cos_alpha = (d12 ** 2 + d13 ** 2 - d23 ** 2) / (2 * d12 * d13)
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    alpha = np.arccos(cos_alpha)
    z3 = z1 + d13 * (np.cos(alpha) + 1j * np.sin(alpha))

    # Find the outer circle that contains all three.
    sol_a, sol_b = both_fourth_circles(k1, k2, k3, z1, z2, z3)
    k_out, z_out = sol_a if sol_a[0] < 0 else sol_b

    # Recenter so the outer circle sits at the origin.
    shift = z_out
    return [
        {"k": k_out, "z": z_out - shift, "depth": 0},
        {"k": k1, "z": z1 - shift, "depth": 0},
        {"k": k2, "z": z2 - shift, "depth": 0},
        {"k": k3, "z": z3 - shift, "depth": 0},
    ]


def recurse(c1, c2, c3, c_prev, depth, out):
    """Recurse into the curvy triangle bounded by c1, c2, c3."""
    if depth > MAX_DEPTH:
        return
    k_new, z_new = fourth_circle(
        c1["k"], c2["k"], c3["k"],
        c1["z"], c2["z"], c3["z"],
        c_prev["k"], c_prev["z"],
    )
    if k_new <= 0:          # don't place another outer-type circle
        return
    if 1 / k_new < MIN_RADIUS:
        return
    c_new = {"k": k_new, "z": z_new, "depth": depth}
    out.append(c_new)
    # Three new curvy triangles to recurse into.
    recurse(c1, c2, c_new, c3, depth + 1, out)
    recurse(c1, c3, c_new, c2, depth + 1, out)
    recurse(c2, c3, c_new, c1, depth + 1, out)


def build_gasket(initial):
    circles = list(initial)
    c_out, c1, c2, c3 = initial
    # Four initial triples; each opens one of the four curvy triangles.
    recurse(c1, c2, c3, c_out, 1, circles)
    recurse(c_out, c1, c2, c3, 1, circles)
    recurse(c_out, c1, c3, c2, 1, circles)
    recurse(c_out, c2, c3, c1, 1, circles)
    return circles


def main():
    initial = initial_configuration(*INITIAL_K)
    circles = build_gasket(initial)

    by_depth = {}
    for c in circles:
        by_depth.setdefault(c["depth"], []).append(c)
    max_d = max(by_depth)
    total = sum(len(v) for v in by_depth.values())
    print(f"Built gasket: {total} circles across {max_d + 1} generations.")

    R = abs(1 / initial[0]["k"])
    fig, ax = plt.subplots(figsize=(FIG_SIZE, FIG_SIZE))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    pad = R * 1.05
    ax.set_xlim(-pad, pad)
    ax.set_ylim(-pad, pad)
    ax.set_aspect("equal")
    ax.axis("off")

    cmap = plt.get_cmap(COLORMAP)
    all_patches = []

    def draw_generation(depth):
        color = cmap(depth / max(max_d, 1))
        new_patches = []
        for c in by_depth.get(depth, []):
            r = abs(1 / c["k"])
            patch = Circle((c["z"].real, c["z"].imag), r,
                           fill=False, edgecolor=color, linewidth=LINE_WIDTH)
            ax.add_patch(patch)
            new_patches.append(patch)
        return new_patches

    def animate(frame):
        if frame <= max_d:
            new = draw_generation(frame)
            all_patches.extend(new)
        return all_patches

    anim = FuncAnimation(
        fig, animate,
        frames=max_d + 1,
        interval=REVEAL_INTERVAL_MS,
        blit=False,
        repeat=False,
    )
    # Keep a reference to anim so the garbage collector doesn't eat it.
    fig._anim = anim
    plt.show()


if __name__ == "__main__":
    main()
