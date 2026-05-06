"""
Riemann Sum Visualizer
======================
Interactive visualization of how discrete rectangle approximations
converge to the true integral as n increases.

Controls:
  - Slider: adjust n (number of rectangles, 1–200)
  - Radio buttons: switch between Left, Midpoint, Right sum rules

f(x) = e^(x/4) · |sin(x)| + 0.5   on  [0, 4π]
The exponential growth means every rule has visible error at low n
and real convergence as n climbs — midpoint running ~2× ahead of left/right.

Part of Dan's math portfolio. Companion to double_pendulum.py.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, RadioButtons

# ── Function & bounds ──────────────────────────────────────────────────────────

def f(x):
    return np.exp(x / 4) * np.abs(np.sin(x)) + 0.5

A, B = 0.0, 4 * np.pi

# High-resolution ground truth
_x_hi = np.linspace(A, B, 1_000_000)
TRUE_INTEGRAL = np.trapezoid(f(_x_hi), _x_hi)

# ── Riemann engine ─────────────────────────────────────────────────────────────

def riemann(n, rule='midpoint'):
    h = (B - A) / n
    if rule == 'left':
        xs = np.linspace(A, B - h, n)
    elif rule == 'right':
        xs = np.linspace(A + h, B, n)
    else:                               # midpoint
        xs = np.linspace(A + h / 2, B - h / 2, n)
    return np.sum(f(xs)) * h, xs, h

# ── Style ──────────────────────────────────────────────────────────────────────

BG        = '#0d1117'
FG        = '#e6edf3'
ACCENT    = '#58a6ff'
RECT_FACE = '#1f6feb'
RECT_EDGE = '#388bfd'
ERR_COL   = '#f78166'
GRID_COL  = '#21262d'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor':   BG,
    'axes.edgecolor':   GRID_COL,
    'axes.labelcolor':  FG,
    'xtick.color':      FG,
    'ytick.color':      FG,
    'text.color':       FG,
    'grid.color':       GRID_COL,
    'grid.linestyle':   '--',
    'grid.alpha':       0.4,
    'font.family':      'monospace',
})

# ── Figure layout ──────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(13, 8))
fig.patch.set_facecolor(BG)

ax_top = fig.add_axes([0.08, 0.38, 0.84, 0.52])   # curve + rectangles
ax_bot = fig.add_axes([0.08, 0.12, 0.84, 0.20])   # convergence
ax_sl  = fig.add_axes([0.18, 0.05, 0.58, 0.025])  # n slider
ax_rb  = fig.add_axes([0.80, 0.01, 0.16, 0.09])   # rule radio
ax_rb.set_facecolor(BG)

# Precompute smooth curve
x_fine = np.linspace(A, B, 2_000)
y_fine = f(x_fine)

# Precompute full error curve (all n, for the convergence plot background)
NS_ALL = np.arange(1, 201)

def all_errors(rule):
    return [abs(riemann(n, rule)[0] - TRUE_INTEGRAL) for n in NS_ALL]

# ── Draw ───────────────────────────────────────────────────────────────────────

def draw(n, rule):
    ax_top.clear()
    ax_bot.clear()

    approx, xs, h = riemann(n, rule)
    error = abs(approx - TRUE_INTEGRAL)

    # Rectangles
    rect_lefts = xs - (h / 2 if rule == 'midpoint' else (h if rule == 'right' else 0))
    for xl, xi in zip(rect_lefts, xs):
        ax_top.add_patch(patches.Rectangle(
            (xl, 0), h, f(xi),
            linewidth=0.5,
            edgecolor=RECT_EDGE,
            facecolor=RECT_FACE,
            alpha=0.55,
            zorder=2,
        ))

    # Curve
    ax_top.plot(x_fine, y_fine, color=FG, lw=2, zorder=5)
    ax_top.fill_between(x_fine, y_fine, alpha=0.07, color=ACCENT, zorder=1)

    # Tick labels as multiples of π
    pi_ticks = np.arange(0, 4.5, 0.5) * np.pi
    pi_labels = ['0', 'π/2', 'π', '3π/2', '2π', '5π/2', '3π', '7π/2', '4π']
    ax_top.set_xticks(pi_ticks)
    ax_top.set_xticklabels(pi_labels, fontsize=8)
    ax_top.set_xlim(A, B)
    ax_top.set_ylim(0, y_fine.max() * 1.15)
    ax_top.set_ylabel('f(x)')
    ax_top.grid(True, zorder=0)
    ax_top.set_title(
        f'n = {n}   ·   {rule} rule   ·   '
        f'approx = {approx:.4f}   ·   '
        f'true = {TRUE_INTEGRAL:.4f}   ·   '
        f'error = {error:.3e}',
        color=FG, fontsize=10, pad=10,
    )

    # Convergence — show all three rules faintly, current rule bright
    colors = {'left': '#8b949e', 'midpoint': '#8b949e', 'right': '#8b949e'}
    colors[rule] = ACCENT
    alphas = {'left': 0.25, 'midpoint': 0.25, 'right': 0.25}
    alphas[rule] = 1.0

    for r in ('left', 'midpoint', 'right'):
        errs = all_errors(r)
        ax_bot.semilogy(NS_ALL, errs, color=colors[r], lw=1.2, alpha=alphas[r],
                        label=r if r == rule else '_nolegend_', zorder=2)

    # Current point
    ax_bot.axvline(n, color=ERR_COL, lw=1, linestyle='--', alpha=0.7, zorder=3)
    ax_bot.scatter([n], [error], color=ERR_COL, s=60, zorder=4)

    ax_bot.set_xlim(1, 200)
    ax_bot.set_xlabel('n  (rectangles)')
    ax_bot.set_ylabel('|error|  (log scale)')
    ax_bot.set_title('Convergence', fontsize=9, pad=6)
    ax_bot.grid(True, zorder=0)
    ax_bot.legend(fontsize=8, facecolor=BG, edgecolor=GRID_COL, labelcolor=FG,
                  loc='upper right')

    fig.canvas.draw_idle()

# ── Widgets ────────────────────────────────────────────────────────────────────

slider = Slider(ax_sl, 'n', 1, 200, valinit=8, valstep=1,
                color=ACCENT, track_color=GRID_COL)
slider.label.set_color(FG)
slider.valtext.set_color(FG)

radio = RadioButtons(ax_rb, ('midpoint', 'left', 'right'), active=0,
                     activecolor=ACCENT)
for lbl in radio.labels:
    lbl.set_color(FG)
    lbl.set_fontsize(8)

# ── Title ──────────────────────────────────────────────────────────────────────

fig.text(0.5, 0.97, 'Riemann Sum Visualizer',
         ha='center', va='top', fontsize=14, fontweight='bold', color=FG)
fig.text(0.5, 0.935,
         'f(x) = e^(x/4) · |sin(x)| + 0.5    on  [0, 4π]',
         ha='center', va='top', fontsize=9, color=ACCENT)

# ── Wire & launch ──────────────────────────────────────────────────────────────

state = {'rule': 'midpoint'}

def on_slider(_):
    draw(int(slider.val), state['rule'])

def on_radio(label):
    state['rule'] = label
    draw(int(slider.val), label)

slider.on_changed(on_slider)
radio.on_clicked(on_radio)

draw(8, 'midpoint')
plt.show()
