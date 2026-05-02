"""
Apollonian Gasket — interactive fractal explorer (v3).

Run this file; a window opens with sliders to play with. Drag the sliders
to new values, then click "Rebuild" to regenerate. Scroll wheel zooms
in/out centered on the cursor. The default matplotlib toolbar also works
(pan, box-zoom, save).

The math: Descartes' Circle Theorem. For four mutually tangent circles
with curvatures (k = 1/radius, negative if the circle contains the others):

    (k1 + k2 + k3 + k4)^2 = 2 * (k1^2 + k2^2 + k3^2 + k4^2)

Given any three mutually tangent circles, two circles are tangent to all
three (one on each side of the curvy triangle they form). Apply recursively.

Requires: numpy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
from matplotlib.widgets import Slider, Button

# ── Knobs ─────────────────────────────────────────────────────────────

# Starting values
DEFAULT_K = (2.0, 2.0, 3.0)   # try (2, 2, 2), (1, 2, 3), (2, 3, 5)...
DEFAULT_MAX_DEPTH = 7
DEFAULT_SPEED = 6             # circles revealed per frame within a generation

# Slider ranges
K_MIN, K_MAX = 0.5, 10.0     # curvature slider bounds
DEPTH_MAX = 14                # max recursion depth the slider can reach
SPEED_MAX = 20                # max circles-per-frame the slider can reach

# Fractal detail
MIN_RADIUS = 0.001            # prune circles smaller than this (raise to reduce count)

# Animation
FADE_FRAMES = 8               # frames each circle takes to fade in
FRAME_INTERVAL_MS = 25        # timer interval (~40 fps)
GAP_FRAMES_BETWEEN_GENS = 4   # pause between generations

# Visuals
COLORMAP = "cividis"         # try: plasma, viridis, magma, inferno, cividis
LINE_WIDTH = 0.9
BG_COLOR = "#0a0a0a"
FIGURE_SIZE = (10, 10)

# ──────────────────────────────────────────────────────────────────────


def fourth_circle(k1, k2, k3, z1, z2, z3, k_prev, z_prev):
    sum_k = k1 + k2 + k3
    sum_kz = k1 * z1 + k2 * z2 + k3 * z3
    k_new = 2 * sum_k - k_prev
    if k_new == 0:
        return 0.0, 0 + 0j
    z_new = (2 * sum_kz - k_prev * z_prev) / k_new
    return k_new, z_new


def both_fourth_circles(k1, k2, k3, z1, z2, z3):
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
    r1, r2, r3 = 1 / k1, 1 / k2, 1 / k3
    z1 = 0 + 0j
    z2 = (r1 + r2) + 0j
    d13 = r1 + r3
    d12 = r1 + r2
    d23 = r2 + r3
    cos_alpha = (d12 ** 2 + d13 ** 2 - d23 ** 2) / (2 * d12 * d13)
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    alpha = np.arccos(cos_alpha)
    z3 = z1 + d13 * (np.cos(alpha) + 1j * np.sin(alpha))

    sol_a, sol_b = both_fourth_circles(k1, k2, k3, z1, z2, z3)
    k_out, z_out = sol_a if sol_a[0] < 0 else sol_b

    shift = z_out
    return [
        {"k": k_out, "z": z_out - shift, "depth": 0},
        {"k": k1, "z": z1 - shift, "depth": 0},
        {"k": k2, "z": z2 - shift, "depth": 0},
        {"k": k3, "z": z3 - shift, "depth": 0},
    ]


def recurse(c1, c2, c3, c_prev, depth, out, max_depth, min_radius):
    if depth > max_depth:
        return
    k_new, z_new = fourth_circle(
        c1["k"], c2["k"], c3["k"],
        c1["z"], c2["z"], c3["z"],
        c_prev["k"], c_prev["z"],
    )
    if k_new <= 0:
        return
    if 1 / k_new < min_radius:
        return
    c_new = {"k": k_new, "z": z_new, "depth": depth}
    out.append(c_new)
    recurse(c1, c2, c_new, c3, depth + 1, out, max_depth, min_radius)
    recurse(c1, c3, c_new, c2, depth + 1, out, max_depth, min_radius)
    recurse(c2, c3, c_new, c1, depth + 1, out, max_depth, min_radius)


def build_gasket(initial, max_depth, min_radius=MIN_RADIUS):
    circles = list(initial)
    c_out, c1, c2, c3 = initial
    recurse(c1, c2, c3, c_out, 1, circles, max_depth, min_radius)
    recurse(c_out, c1, c2, c3, 1, circles, max_depth, min_radius)
    recurse(c_out, c1, c3, c2, 1, circles, max_depth, min_radius)
    recurse(c_out, c2, c3, c1, 1, circles, max_depth, min_radius)
    return circles


def plan_reveal(circles_by_depth, circles_per_frame):
    plan = []
    frame = 0
    for depth in sorted(circles_by_depth.keys()):
        circs = sorted(circles_by_depth[depth], key=lambda c: -abs(1 / c["k"]))
        gen_start = frame
        for i, c in enumerate(circs):
            plan.append((c, gen_start + i // max(circles_per_frame, 1)))
        frame = plan[-1][1] + GAP_FRAMES_BETWEEN_GENS
    return plan


class GasketApp:
    def __init__(self):
        self.fig = plt.figure(figsize=FIGURE_SIZE, facecolor=BG_COLOR)
        self.ax = self.fig.add_axes([0.05, 0.26, 0.90, 0.71])
        self.ax.set_facecolor(BG_COLOR)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        slider_bg = "#1a1a1a"
        self.s_k1 = Slider(self.fig.add_axes([0.15, 0.20, 0.65, 0.02], facecolor=slider_bg),
                           'k\u2081', K_MIN, K_MAX, valinit=DEFAULT_K[0], color="#7f9fff")
        self.s_k2 = Slider(self.fig.add_axes([0.15, 0.17, 0.65, 0.02], facecolor=slider_bg),
                           'k\u2082', K_MIN, K_MAX, valinit=DEFAULT_K[1], color="#7f9fff")
        self.s_k3 = Slider(self.fig.add_axes([0.15, 0.14, 0.65, 0.02], facecolor=slider_bg),
                           'k\u2083', K_MIN, K_MAX, valinit=DEFAULT_K[2], color="#7f9fff")
        self.s_depth = Slider(self.fig.add_axes([0.15, 0.11, 0.65, 0.02], facecolor=slider_bg),
                              'depth', 1, DEPTH_MAX, valinit=DEFAULT_MAX_DEPTH, valstep=1, color="#ff9f7f")
        self.s_speed = Slider(self.fig.add_axes([0.15, 0.08, 0.65, 0.02], facecolor=slider_bg),
                              'speed', 1, SPEED_MAX, valinit=DEFAULT_SPEED, valstep=1, color="#7fcf9f")

        for s in [self.s_k1, self.s_k2, self.s_k3, self.s_depth, self.s_speed]:
            s.label.set_color("#cccccc")
            s.valtext.set_color("#cccccc")

        for s in [self.s_k1, self.s_k2, self.s_k3]:
            s.on_changed(self._update_values_label)

        self.btn_rebuild = Button(self.fig.add_axes([0.82, 0.03, 0.12, 0.04]),
                                  'Rebuild', color="#2b2b2b", hovercolor="#4a4a4a")
        self.btn_rebuild.label.set_color("#eeeeee")
        self.btn_rebuild.on_clicked(self._on_rebuild)

        self.btn_reset = Button(self.fig.add_axes([0.68, 0.03, 0.12, 0.04]),
                                'Reset', color="#2b2b2b", hovercolor="#4a4a4a")
        self.btn_reset.label.set_color("#eeeeee")
        self.btn_reset.on_clicked(self._on_reset)

        self.btn_fit = Button(self.fig.add_axes([0.54, 0.03, 0.12, 0.04]),
                              'Fit view', color="#2b2b2b", hovercolor="#4a4a4a")
        self.btn_fit.label.set_color("#eeeeee")
        self.btn_fit.on_clicked(self._on_fit)

        self.circle_count_text = self.fig.text(
            0.01, 0.845, "",
            fontsize=9, color='white', alpha=0.55,
            va='top', ha='left',
            math_fontfamily='cm',
        )
        self.status = self.fig.text(0.05, 0.035, "", color="#888888", fontsize=9)

        self.theorem_text = self.fig.text(
            0.01, 0.955,
            r'$(k_1+k_2+k_3+k_4)^2 = 2(k_1^2+k_2^2+k_3^2+k_4^2)$',
            fontsize=11, color='white', alpha=0.35,
            va='top', ha='left',
            math_fontfamily='cm',
            fontweight='semibold',
        )
        self.values_text = self.fig.text(
            0.01, 0.895,
            '',
            fontsize=9, color='white', alpha=0.55,
            va='top', ha='left',
            math_fontfamily='cm',
        )
        self.quote_text = self.fig.text(
            0.99, 0.948,
            "Any three tangent circles have exactly two more that\n"
            "are tangent to all three: one in the space between,\n"
            "one wrapping around. The gasket: take the wrapper as\n"
            "boundary, then drop the in-between circle into every\n"
            "space, forever.",
            fontsize=8, color='white', alpha=0.35,
            va='top', ha='right',
            math_fontfamily='cm',
            fontweight='semibold',
        )

        self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)
        self.fig.canvas.mpl_connect("button_press_event", self._on_val_click)

        self._edit_ax = None
        self._edit_text_artist = None
        self._input_text = ""
        self._key_cid = None
        self._edit_slider = None
        self._edit_vmin = 0.0
        self._edit_vmax = 1.0
        self._edit_is_int = False
        self._sliders_info = [
            (self.s_k1,    K_MIN, K_MAX,    False),
            (self.s_k2,    K_MIN, K_MAX,    False),
            (self.s_k3,    K_MIN, K_MAX,    False),
            (self.s_depth, 1,     DEPTH_MAX, True),
            (self.s_speed, 1,     SPEED_MAX, True),
        ]

        self.cmap = plt.get_cmap(COLORMAP)
        self.reveal_info = []
        self._collection = None
        self.frame = 0
        self.max_frame = 0
        self.R = 1.0

        # timer-driven animation (widget-friendly; avoids FuncAnimation event grab)
        self.timer = self.fig.canvas.new_timer(interval=FRAME_INTERVAL_MS)
        self.timer.add_callback(self._on_tick)

        self._update_values_label()
        self._build_gasket()
        self.timer.start()

    def _on_rebuild(self, event):
        print(f"[rebuild] k=({self.s_k1.val:.2f}, {self.s_k2.val:.2f}, "
              f"{self.s_k3.val:.2f})  depth={int(self.s_depth.val)}  "
              f"speed={int(self.s_speed.val)}")
        self._build_gasket()

    def _on_reset(self, event):
        self.s_k1.reset()
        self.s_k2.reset()
        self.s_k3.reset()
        self.s_depth.reset()
        self.s_speed.reset()
        self._build_gasket()

    def _on_fit(self, event):
        self.fit_view()

    def _update_values_label(self, _=None):
        k1, k2, k3 = self.s_k1.val, self.s_k2.val, self.s_k3.val
        disc = max(k1 * k2 + k2 * k3 + k3 * k1, 0.0)
        k4 = k1 + k2 + k3 - 2 * np.sqrt(disc)
        self.values_text.set_text(
            f'$k_1={k1:.2f},\\ k_2={k2:.2f},\\ k_3={k3:.2f}$\n'
            f'$k_4={k4:.3f}$  (outer circle)'
        )
        self.fig.canvas.draw_idle()

    def _build_gasket(self):
        if self._collection is not None:
            self._collection.remove()
            self._collection = None
        self.reveal_info = []
        self.frame = 0

        k1 = float(self.s_k1.val)
        k2 = float(self.s_k2.val)
        k3 = float(self.s_k3.val)
        max_depth = int(self.s_depth.val)
        speed = int(self.s_speed.val)

        try:
            initial = initial_configuration(k1, k2, k3)
        except Exception as e:
            self.status.set_text(f"Invalid curvatures: {e}")
            self.fig.canvas.draw_idle()
            return

        circles = build_gasket(initial, max_depth=max_depth)

        by_depth = {}
        for c in circles:
            by_depth.setdefault(c["depth"], []).append(c)
        max_d = max(by_depth)

        R = abs(1 / initial[0]["k"])
        self.R = R
        self.fit_view()

        plan = plan_reveal(by_depth, circles_per_frame=speed)
        self.max_frame = (plan[-1][1] + FADE_FRAMES) if plan else 1

        patches = [Circle((c["z"].real, c["z"].imag), abs(1 / c["k"])) for c, _ in plan]
        base_rgba = np.array([self.cmap(c["depth"] / max(max_d, 1)) for c, _ in plan])
        self._reveal_frames = np.array([rf for _, rf in plan], dtype=float)

        # working RGBA buffer: RGB from colormap, alpha starts at 0
        self._current_rgba = base_rgba.copy()
        self._current_rgba[:, 3] = 0.0
        # keep full-opacity RGB for tick updates
        self._base_rgb = base_rgba[:, :3]

        self._collection = PatchCollection(patches, facecolor="none",
                                           edgecolors=self._current_rgba,
                                           linewidths=LINE_WIDTH)
        self.ax.add_collection(self._collection)

        self.circle_count_text.set_text(f"{len(circles):,} circles drawn")
        self.status.set_text(
            f"{max_d + 1} generations  \u00b7  "
            f"scroll to zoom, drag + Rebuild to reshape"
        )
        self.fig.canvas.draw_idle()

    def _on_tick(self):
        if self.frame > self.max_frame:
            return
        alphas = np.clip((self.frame - self._reveal_frames) / FADE_FRAMES, 0.0, 1.0)
        self._current_rgba[:, :3] = self._base_rgb
        self._current_rgba[:, 3] = alphas
        self._collection.set_edgecolors(self._current_rgba)
        self.frame += 1
        self.fig.canvas.draw_idle()

    def fit_view(self):
        pad = self.R * 1.05
        self.ax.set_xlim(-pad, pad)
        self.ax.set_ylim(-pad, pad)
        self.fig.canvas.draw_idle()

    def on_scroll(self, event):
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        scale = 1.2 if event.button == "down" else 1 / 1.2
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()
        xd, yd = event.xdata, event.ydata
        self.ax.set_xlim(xd - (xd - xmin) * scale, xd + (xmax - xd) * scale)
        self.ax.set_ylim(yd - (yd - ymin) * scale, yd + (ymax - yd) * scale)
        self.fig.canvas.draw_idle()

    def _on_val_click(self, event):
        try:
            renderer = self.fig.canvas.get_renderer()
        except AttributeError:
            return
        for slider, vmin, vmax, is_int in self._sliders_info:
            bbox = slider.valtext.get_window_extent(renderer=renderer)
            if bbox.expanded(1.4, 1.8).contains(event.x, event.y):
                self._open_val_editor(slider, vmin, vmax, is_int)
                return
        if self._edit_ax is not None and event.inaxes != self._edit_ax:
            self._close_val_editor()

    def _open_val_editor(self, slider, vmin, vmax, is_int):
        self._close_val_editor()
        try:
            renderer = self.fig.canvas.get_renderer()
        except AttributeError:
            return
        bbox = slider.valtext.get_window_extent(renderer=renderer)
        inv = self.fig.transFigure.inverted()
        cx = (bbox.x0 + bbox.x1) / 2
        cy = (bbox.y0 + bbox.y1) / 2
        w_d = max(bbox.width * 1.6, 58)
        h_d = max(bbox.height * 1.8, 18)
        bl = inv.transform((cx - w_d / 2, cy - h_d / 2))
        tr = inv.transform((cx + w_d / 2, cy + h_d / 2))
        rect = [bl[0], bl[1], tr[0] - bl[0], tr[1] - bl[1]]

        ax_ed = self.fig.add_axes(rect, facecolor="#1e1e1e", label="_val_editor")
        ax_ed.set_zorder(10)
        ax_ed.axis("off")
        for spine in ax_ed.spines.values():
            spine.set_edgecolor("#555555")
            spine.set_linewidth(1)
        ax_ed.set_axis_on()

        self._input_text = str(int(slider.val)) if is_int else f"{slider.val:.2f}"
        self._edit_text_artist = ax_ed.text(
            0.5, 0.5, self._input_text + "│",
            transform=ax_ed.transAxes,
            color="white", fontsize=9,
            va="center", ha="center",
        )
        self._edit_ax = ax_ed
        self._edit_slider = slider
        self._edit_vmin = vmin
        self._edit_vmax = vmax
        self._edit_is_int = is_int
        self._key_cid = self.fig.canvas.mpl_connect("key_press_event", self._on_edit_key)
        self.fig.canvas.draw_idle()

    def _update_edit_display(self):
        if self._edit_text_artist is not None:
            self._edit_text_artist.set_text(self._input_text + "│")
            self.fig.canvas.draw_idle()

    def _submit_edit(self):
        try:
            v = float(self._input_text)
            v = float(np.clip(v, self._edit_vmin, self._edit_vmax))
            if self._edit_is_int:
                v = int(round(v))
            self._edit_slider.set_val(v)
        except ValueError:
            pass
        self._close_val_editor()

    def _on_edit_key(self, event):
        key = event.key
        if key in ("enter", "return"):
            self._submit_edit()
        elif key == "escape":
            self._close_val_editor()
        elif key == "backspace":
            self._input_text = self._input_text[:-1]
            self._update_edit_display()
        elif key in ("delete", "ctrl+a"):
            self._input_text = ""
            self._update_edit_display()
        elif key and len(key) == 1:
            if key.isdigit():
                self._input_text += key
                self._update_edit_display()
            elif key == "." and "." not in self._input_text and not self._edit_is_int:
                self._input_text += key
                self._update_edit_display()
            elif key == "-" and not self._input_text:
                self._input_text += key
                self._update_edit_display()

    def _close_val_editor(self):
        if self._key_cid is not None:
            self.fig.canvas.mpl_disconnect(self._key_cid)
            self._key_cid = None
        if self._edit_ax is not None:
            self._edit_ax.remove()
            self._edit_ax = None
            self._edit_text_artist = None
            self.fig.canvas.draw_idle()


_app = None  # module-level reference to prevent GC


def main():
    global _app
    _app = GasketApp()
    plt.show()


if __name__ == "__main__":
    main()
