import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import solve_ivp

# Parameters for the double pendulum
L1, L2 = .5, 1.0   # Lengths of pendulums (meters)
m1, m2 = 1.0, .5   # Masses of pendulum bobs (kg)
g = 9.81          # Acceleration due to gravity (m/s^2)

# Equations of motion
def equations(t, y):
    theta1, z1, theta2, z2 = y
    delta = theta2 - theta1

    denominator1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta)**2
    denominator2 = (L2 / L1) * denominator1

    dydt = np.zeros_like(y)
    dydt[0] = z1
    dydt[1] = (
        m2 * L1 * z1**2 * np.sin(delta) * np.cos(delta) +
        m2 * g * np.sin(theta2) * np.cos(delta) +
        m2 * L2 * z2**2 * np.sin(delta) -
        (m1 + m2) * g * np.sin(theta1)
    ) / denominator1
    dydt[2] = z2
    dydt[3] = (
        -m2 * L2 * z2**2 * np.sin(delta) * np.cos(delta) +
        (m1 + m2) * g * np.sin(theta1) * np.cos(delta) -
        (m1 + m2) * L1 * z1**2 * np.sin(delta) -
        (m1 + m2) * g * np.sin(theta2)
    ) / denominator2
    return dydt

# Initial conditions: [theta1, theta1_dot, theta2, theta2_dot]
y0 = [np.pi / 1, 0, np.pi / 4, 0]

# Time span for the simulation
t_span = (0, 20)
t_eval = np.linspace(t_span[0], t_span[1], 1000)

# Solve the differential equations
solution = solve_ivp(equations, t_span, y0, t_eval=t_eval, method='RK45')

theta1 = solution.y[0]
theta2 = solution.y[2]

# Convert to Cartesian coordinates
x1 = L1 * np.sin(theta1)
y1 = -L1 * np.cos(theta1)
x2 = x1 + L2 * np.sin(theta2)
y2 = y1 - L2 * np.cos(theta2)

# Set up the figure and axis
fig, ax = plt.subplots()
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-2.5, 2.5)
ax.set_aspect('equal')
ax.grid()

# Plot elements
line, = ax.plot([], [], 'o-', lw=2, color='blue')
trace, = ax.plot([], [], '-', lw=1, color='red')
x_trace, y_trace = [], []

# Animation function
def update(frame):
    line.set_data([0, x1[frame], x2[frame]], [0, y1[frame], y2[frame]])
    x_trace.append(x2[frame])
    y_trace.append(y2[frame])
    trace.set_data(x_trace, y_trace)
    return line, trace

ani = FuncAnimation(fig, update, frames=len(t_eval), interval=20, blit=True)

plt.show()
