import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from scipy.integrate import solve_ivp

plt.style.use('dark_background')
plt.rcParams['font.family'] = 'serif'

#--- knobs ---

L1, L2 = 0.5, 1.0
m1, m2 = 1.0, 0.5
g = 9.81

def equations(t, y):
    theta1, z1, theta2, z2 = y
    delta = theta2 - theta1
    denom1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta)**2
    denom2 = (L2 / L1) * denom1
    dydt = np.zeros(4)
    dydt[0] = z1
    dydt[1] = (
        m2 * L1 * z1**2 * np.sin(delta) * np.cos(delta) +
        m2 * g * np.sin(theta2) * np.cos(delta) +
        m2 * L2 * z2**2 * np.sin(delta) -
        (m1 + m2) * g * np.sin(theta1)
    ) / denom1
    dydt[2] = z2
    dydt[3] = (
        -m2 * L2 * z2**2 * np.sin(delta) * np.cos(delta) +
        (m1 + m2) * g * np.sin(theta1) * np.cos(delta) -
        (m1 + m2) * L1 * z1**2 * np.sin(delta) -
        (m1 + m2) * g * np.sin(theta2)
    ) / denom2
    return dydt

def run_simulation(theta1_0, theta2_0, z1_0=0.0, z2_0=0.0):
    y0 = [theta1_0, z1_0, theta2_0, z2_0]
    sol = solve_ivp(
        equations, (0, 20), y0,
        t_eval=np.linspace(0, 20, 2000),
        method='RK45', max_step=0.01,
    )
    t1, t2 = sol.y[0], sol.y[2]
    x1 = L1 * np.sin(t1);  y1 = -L1 * np.cos(t1)
    x2 = x1 + L2 * np.sin(t2);  y2 = y1 - L2 * np.cos(t2)
    return x1, y1, x2, y2

sim = dict(
    x1=None, y1=None, x2=None, y2=None,
    frame=0, x_trace=[], y_trace=[],
    dragging=False, drag_bob=None,
    theta1=np.pi, theta2=np.pi / 4,
)

def restart(theta1=None, theta2=None):
    if theta1 is not None: sim['theta1'] = theta1
    if theta2 is not None: sim['theta2'] = theta2
    x1, y1, x2, y2 = run_simulation(sim['theta1'], sim['theta2'])
    sim.update(x1=x1, y1=y1, x2=x2, y2=y2, frame=0)
    sim['x_trace'].clear()
    sim['y_trace'].clear()

restart()

# ── Layout ───────────────────────────────────────────────────────────
BG = '#0e0e12'
fig = plt.figure(figsize=(14, 8), facecolor=BG)
gs = gridspec.GridSpec(
    1, 2, width_ratios=[3, 2], wspace=0.0,
    left=0.02, right=0.98, top=0.95, bottom=0.08,
)
ax    = fig.add_subplot(gs[0])
ax_eq = fig.add_subplot(gs[1])

ax.set_facecolor(BG)
ax.set_xlim(-2, 2)
ax.set_ylim(-2.2, 0.8)
ax.set_aspect('equal')
ax.grid(True, alpha=0.12, color='#888888')
ax.tick_params(colors='#555555', labelsize=8)
for sp in ax.spines.values():
    sp.set_color('#2a2a2a')
ax.set_title('Double Pendulum', color='#e0e0e0', fontsize=15, pad=10)

ax_eq.set_facecolor(BG)
ax_eq.axis('off')

# ── Equations panel ──────────────────────────────────────────────────
def teq(y, s, size=10, color='#d0d0d0', **kw):
    ax_eq.text(0.05, y, s, transform=ax_eq.transAxes,
               fontsize=size, color=color, va='top', **kw)

teq(0.97, 'Equations of Motion', size=13, color='#f0f0f0', fontweight='bold')

teq(0.88, r'$\delta = \theta_2 - \theta_1$')
teq(0.81, r'$\Delta = (m_1+m_2)\,L_1 - m_2\,L_1\cos^2\delta$')

teq(0.72, r'$\ddot{\theta}_1 = \frac{1}{\Delta}\ [$', size=11)
teq(0.65, r'$\quad m_2 L_1\,\dot{\theta}_1^2 \sin\delta\cos\delta$',  color='#aaaaaa')
teq(0.59, r'$\quad +\; m_2 g \sin\theta_2\cos\delta$',                color='#aaaaaa')
teq(0.53, r'$\quad +\; m_2 L_2\,\dot{\theta}_2^2 \sin\delta$',        color='#aaaaaa')
teq(0.47, r'$\quad -\; (m_1+m_2)\,g\sin\theta_1\ ]$',             color='#aaaaaa')

teq(0.39, r'$\ddot{\theta}_2 = \frac{L_1}{L_2\,\Delta}\ [$', size=11)
teq(0.32, r'$\quad -\,m_2 L_2\,\dot{\theta}_2^2 \sin\delta\cos\delta$',      color='#aaaaaa')
teq(0.26, r'$\quad +\;(m_1+m_2)\,g\sin\theta_1\cos\delta$',                  color='#aaaaaa')
teq(0.20, r'$\quad -\;(m_1+m_2)\,L_1\dot{\theta}_1^2\sin\delta$',            color='#aaaaaa')
teq(0.14, r'$\quad -\;(m_1+m_2)\,g\sin\theta_2\ ]$',                     color='#aaaaaa')

teq(0.06, f'$L_1={L1}$ m  $L_2={L2}$ m  $m_1={m1}$ kg  $m_2={m2}$ kg',
    size=9, color='#777777')
teq(0.01, 'drag a bob to reposition  ·  random start button below',
    size=8, color='#444444', style='italic')

# ── Animation elements ───────────────────────────────────────────────
ax.plot([0], [0], 'o', ms=6, color='#666666', zorder=5)
arm,   = ax.plot([], [], '-',  lw=2.5, color='#4fc3f7', zorder=2)
bob1,  = ax.plot([], [], 'o', ms=12,  color='#4fc3f7', zorder=4)
bob2,  = ax.plot([], [], 'o', ms=16,  color='#ff7043', zorder=4)
trace, = ax.plot([], [], '-',  lw=0.7, color='#ff7043', alpha=0.4, zorder=1)

def set_positions(x1v, y1v, x2v, y2v):
    arm.set_data([0, x1v, x2v], [0, y1v, y2v])
    bob1.set_data([x1v], [y1v])
    bob2.set_data([x2v], [y2v])

def update(_):
    if sim['dragging']:
        return
    i = sim['frame']
    n = len(sim['x1'])
    if i >= n:
        sim['frame'] = 0
        sim['x_trace'].clear()
        sim['y_trace'].clear()
        return
    x1v, y1v = sim['x1'][i], sim['y1'][i]
    x2v, y2v = sim['x2'][i], sim['y2'][i]
    set_positions(x1v, y1v, x2v, y2v)
    sim['x_trace'].append(x2v)
    sim['y_trace'].append(y2v)
    if len(sim['x_trace']) > 500:
        sim['x_trace'].pop(0)
        sim['y_trace'].pop(0)
    trace.set_data(sim['x_trace'], sim['y_trace'])
    sim['frame'] += 1

# ── Mouse interaction ────────────────────────────────────────────────
HIT = 0.15

def on_press(event):
    if event.inaxes != ax or event.xdata is None:
        return
    mx, my = event.xdata, event.ydata
    i = min(sim['frame'], len(sim['x1']) - 1)
    if np.hypot(mx - sim['x2'][i], my - sim['y2'][i]) < HIT:
        sim.update(dragging=True, drag_bob=2)
    elif np.hypot(mx - sim['x1'][i], my - sim['y1'][i]) < HIT:
        sim.update(dragging=True, drag_bob=1)

def on_motion(event):
    if not sim['dragging'] or event.inaxes != ax or event.xdata is None:
        return
    mx, my = event.xdata, event.ydata
    i = min(sim['frame'], len(sim['x1']) - 1)
    if sim['drag_bob'] == 1:
        th1 = np.arctan2(mx, -my)
        x1v, y1v = L1 * np.sin(th1), -L1 * np.cos(th1)
        th2 = np.arctan2(sim['x2'][i] - sim['x1'][i], -(sim['y2'][i] - sim['y1'][i]))
        x2v, y2v = x1v + L2 * np.sin(th2), y1v - L2 * np.cos(th2)
    else:
        x1v, y1v = sim['x1'][i], sim['y1'][i]
        th2 = np.arctan2(mx - x1v, -(my - y1v))
        x2v, y2v = x1v + L2 * np.sin(th2), y1v - L2 * np.cos(th2)
    set_positions(x1v, y1v, x2v, y2v)
    fig.canvas.draw_idle()

def on_release(event):
    if not sim['dragging']:
        return
    sim['dragging'] = False
    if event.inaxes != ax or event.xdata is None:
        sim['drag_bob'] = None
        return
    mx, my = event.xdata, event.ydata
    i = min(sim['frame'], len(sim['x1']) - 1)
    if sim['drag_bob'] == 1:
        th1 = np.arctan2(mx, -my)
        th2 = np.arctan2(sim['x2'][i] - sim['x1'][i], -(sim['y2'][i] - sim['y1'][i]))
    else:
        th1 = np.arctan2(sim['x1'][i], -sim['y1'][i])
        th2 = np.arctan2(mx - sim['x1'][i], -(my - sim['y1'][i]))
    sim['drag_bob'] = None
    restart(theta1=th1, theta2=th2)

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# ── Random start button ──────────────────────────────────────────────
ax_btn = fig.add_axes([0.64, 0.015, 0.14, 0.05])
btn = Button(ax_btn, 'Random Start', color='#1a1a2a', hovercolor='#252545')
btn.label.set_color('#cccccc')
btn.label.set_fontsize(10)

def on_random(_):
    restart(
        theta1=np.random.uniform(-np.pi, np.pi),
        theta2=np.random.uniform(-np.pi, np.pi),
    )

btn.on_clicked(on_random)

ani = FuncAnimation(fig, update, interval=20, blit=False, cache_frame_data=False)
plt.show()
