from dft_draft2 import DynamicField, gaussian_input
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

field = DynamicField(
     name = 'color__space',
            size = (50,200),
            h=-6.0, tau=80.0,
            sigma_exc=4.0, a_exc=0.7,
            sigma_inh=10.0, a_inh=0.3
)

x = np.arange(field.size[0])
y = np.arange(field.size[1])

stim_left_blue =  gaussian_input(x, center=40, sigma=3.0, amplitude=8.0)
stim_right_red =  gaussian_input(x, center=10, sigma=3.0, amplitude=8.0)
stim_left_space =  gaussian_input(y, center=60, sigma=5.0, amplitude=8.0)
stim_right_space =  gaussian_input(y, center=140, sigma=5.0, amplitude=8.0)

stim_left = np.outer(stim_left_blue, stim_left_space)
stim_right = np.outer(stim_right_red, stim_right_space)

stim_input = stim_left + stim_right

steps_per_frame = 10
n_encode_frames = 400  # 4000ms
n_delay_frames = 250    # 2500ms middle input added, side inputs removed
n_total_frames = n_encode_frames + n_delay_frames

fig, ax = plt.subplots(figsize=(12,5))

img = ax.imshow(field.u, aspect="auto", cmap='RdBu_r',vmin = -8, vmax = 15, origin = 'lower')

ax.set_xlabel("Space")
ax.set_ylabel("Color")
fig.colorbar(img, ax=ax, label='Activation')

time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                     fontsize=12, fontweight='bold',
                     verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

def get_phase(frame):
    if frame < n_encode_frames:
        elapsed = frame * steps_per_frame
        return f'ENCODING  t={elapsed}ms', stim_input
    else:
        elapsed = (frame - n_encode_frames) * steps_per_frame + 4000
        return f'DELAY  t={elapsed}ms', None
    

def update(frame):
    phase_label, current_input = get_phase(frame)

    for step in range(steps_per_frame):
        field.step(current_input)

    img.set_data(field.u)

    time_text.set_text(phase_label)

    return img, time_text

ani = FuncAnimation(fig, update, frames=n_total_frames,
                    interval=20, blit=True, repeat=False)
plt.show()

