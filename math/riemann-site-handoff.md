# CLI Handoff — Riemann Sum Interactive Site
_Written by EVA · 2026-05-05 · Deliver to Claude CLI alongside `riemann_sum.py`_

---

## What this is

Convert the attached Python/matplotlib Riemann Sum visualizer into a single self-contained HTML file in the style of double_pendulum.html — dark aesthetic, canvas-based, no framework, no instructions, just the math and the controls.

This will be the second entry on the Neal.fun-style math portfolio site (see double_pendulum.html for the established aesthetic). The Python script is the reference implementation for the math. You're porting the logic and adding richer interactivity.

---

## Reference file

`riemann_sum.py` (in the same directory as this handoff) — read it in full before writing anything. The core math is:

- Function: `f(x) = e^(x/4) · |sin(x)| + 0.5` on `[0, 4π]`
- Three sum rules: left endpoint, right endpoint, midpoint
- True integral computed via high-resolution numerical integration
- Two panels: rectangle visualization (top) + error convergence (bottom, log scale)

The HTML version should preserve this structure and extend it.

---

## What to build

### Function selector — 5 functions, switchable via pill tabs or a dropdown

| Name | Formula | Domain | Parameters |
|---|---|---|---|
| Power | `x^p` | [0, 1] | `p` (0.1 → 4) |
| Beta | `x^a · (1−x)^b` | [0, 1] | `a` (0.5 → 5), `b` (0.5 → 5) |
| Harmonic | `e^(x/4) · \|sin(kx)\| + 0.5` | [0, 4π] | `k` (1 → 6) |
| Gaussian | `e^(−(x−μ)²/2σ²)` | [μ−4σ, μ+4σ] | `μ` (0 → 1), `σ` (0.05 → 0.5) |
| Beat | `\|sin(x) · sin(2x) · sin(3x)\|` | [0, 2π] | none |

Each function should recompute the true integral numerically when selected or when its parameters change. The true integral is always computed at very high resolution (≥50,000 points) — it's the ground truth the error panel measures against.

### Controls

- **n slider** — number of rectangles, 1 to 300. Drag feels responsive; rectangles redraw live.
- **Rule toggle** — Left / Midpoint / Right as three buttons, one active at a time.
- **Function tabs** — switch between the 5 functions above. Switching resets n to a sensible default (16).
- **Parameter sliders** — shown only for the active function. Changing a parameter rerenders everything including the ground truth. Animate smoothly if possible.

### Panels

**Top — curve + rectangles:**
- Draw the smooth curve (high resolution)
- Draw Riemann rectangles in the current color, semi-transparent
- Show a faint fill under the curve
- Display live: n, rule, approximation value, true value, absolute error, % error

**Bottom — convergence:**
- Log-scale error vs. n, 1 to 300
- All three rules shown simultaneously: Left (faint), Right (faint), Midpoint (faint)
- Active rule highlighted in full color
- Current n marked with a vertical line and a dot
- Recomputes when function or parameters change

### Aesthetic — match double_pendulum.html exactly

- Background: `#0d1117`
- Text/lines: `#e6edf3`
- Accent/active: `#58a6ff`
- Rectangle fill: `#1f6feb` at ~50% opacity, edge `#388bfd`
- Error marker: `#f78166`
- Font: monospace
- No labels saying "drag the slider" or "click here." The controls are self-evident.
- Title at top, formula for active function shown in accent color below it
- Mobile-aware but desktop-first

---

## Technical notes

- Single HTML file, no external dependencies except a CDN-hosted math library if needed for display (prefer pure canvas + JS over importing anything heavy)
- True integral: use adaptive Simpson's rule or simple high-resolution trapezoid at 100,000 points — either is fine, accuracy to 6 decimal places is the target
- The convergence panel recomputes errors for all n from 1 to 300 on function/parameter change — this is ~900 sum evaluations, should be instant in JS
- Rectangles are drawn as canvas fillRect calls, not SVG — stays fast at n=300
- Save to: `C:\Users\andre\code\Previous-Coding-Adventures\riemann_sum.html`

---

## What not to do

- Don't add tooltips, help text, or onboarding
- Don't use React, Vue, or any component framework
- Don't add animations that run on their own — everything is user-driven
- Don't replicate the Python script verbatim — the JS should be clean and idiomatic, not a direct translation

---

## The feel

At n=4, the Beta function with a=0.5, b=5 looks absurd — giant rectangles missing a sharp spike entirely. At n=200 it's tight. That's the thing. The user should be able to feel the approximation becoming real. The parameter sliders are there so it feels like a creative space, not a textbook diagram.

_EVA out._
