import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define the function z(Θ)
def z(theta):
    return np.exp(1j * theta) + np.exp(1j * np.pi * theta)

# Create a range of Θ values
theta = np.linspace(0, 200 * np.pi, 10000)  # Adjust range as needed
z_values = z(theta)

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.axhline(0, color='gray', linewidth=0.1)
ax.axvline(0, color='gray', linewidth=0.1)
ax.set_xlabel("Real Part")
ax.set_ylabel("Imaginary Part")
ax.set_title("Animated Plot of $z(\\Theta)$ over Time")
line, = ax.plot([], [], lw=.5)

# Initialization function for the animation
def init():
    line.set_data([], [])
    return line,

# Update function for each frame
def update(frame):
    # Plot the z(Θ) values up to the current frame
    line.set_data(z_values.real[:frame], z_values.imag[:frame])
    return line,

# Create the animation
ani = FuncAnimation(fig, update, frames=len(theta), init_func=init, blit=True, interval=1)

# Display the animation
plt.show()

