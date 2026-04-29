from dft_draft2 import DynamicField, gaussian_input
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

field = DynamicField(
     name = 'color__space',
            size = (200,200),
            h=-6.0, tau=80.0,
            sigma_exc=4.5, a_exc=0.7,
            sigma_inh=7.0, a_inh=0.35
)

x = np.arange(field.size[0])
y = np.arange(field.size[1])

stim_blue =  gaussian_input(x, center=140, sigma=3.0, amplitude=8.0)
stim_red =  gaussian_input(x, center=60, sigma=3.0, amplitude=8.0)
stim_left_space =  gaussian_input(y, center=60, sigma=3.0, amplitude=8.0)
stim_right_space =  gaussian_input(y, center=140, sigma=3.0, amplitude=8.0)


fstim_left_blue = np.outer(stim_blue, stim_left_space)
fstim_right_red = np.outer(stim_red, stim_right_space)

fstim_left_red = np.outer(stim_red, stim_left_space)
fstim_right_blue = np.outer(stim_blue, stim_right_space)

stim_input_1 = fstim_left_blue + fstim_right_red

stim_input_2 = fstim_left_red + fstim_right_blue

steps_per_frame = 10
n_encode_1_frames = 200  # 4000ms
n_delay_frames = 200    # 2500ms middle input added, side inputs removed
n_encode_2_frames = 200
n_delay_2_frames = 200
n_total_frames = n_encode_1_frames + n_delay_frames + n_encode_2_frames + n_delay_2_frames

fig, axes = plt.subplots(3, 1, figsize=(12, 10),
                          gridspec_kw={'height_ratios': [3, 1, 1]})
fig.suptitle('Color x Space Field', fontsize=14)

# Top: 2D heatmap (what you already have)
img = axes[0].imshow(field.u, aspect='auto', cmap='RdBu_r',
                      vmin=-8, vmax=15, origin='lower')
axes[0].set_xlabel('Space')
axes[0].set_ylabel('Color')
fig.colorbar(img, ax=axes[0], label='Activation')

time_text = axes[0].text(0.02, 0.95, '', transform=axes[0].transAxes,
                          fontsize=12, fontweight='bold',
                          verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))



x_space = np.arange(field.size[1])
line_space, = axes[1].plot(x_space, np.zeros(field.size[1]), 'b-', linewidth=2)
axes[1].set_ylim(-0.1, 1.5)
axes[1].set_ylabel('Summed output')
axes[1].set_xlabel('Space')
axes[1].set_title('Spatial readout (sum across color)')
axes[1].axvline(x=60, color='green', linestyle=':', alpha=0.5, label='Left (60)')
axes[1].axvline(x=140, color='orange', linestyle=':', alpha=0.5, label='Right (140)')
axes[1].legend()

# Bottom: color output (collapse across space)
x_color = np.arange(field.size[0])
line_color, = axes[2].plot(x_color, np.zeros(field.size[0]), 'r-', linewidth=2)
axes[2].set_ylim(-0.1, 1.5)
axes[2].set_ylabel('Summed output')
axes[2].set_xlabel('Color')
axes[2].set_title('Color readout (sum across space)')
axes[2].axvline(x=10, color='red', linestyle=':', alpha=0.5, label='Red (10)')
axes[2].axvline(x=40, color='blue', linestyle=':', alpha=0.5, label='Blue (40)')
axes[2].legend()

plt.tight_layout()

def get_phase(frame):
    elapsed = frame * steps_per_frame  # total simulation steps so far

    if frame < n_encode_1_frames:
        return f'ENCODE 1  t={elapsed}', stim_input_1
    elif frame < n_encode_1_frames + n_delay_frames:
        return f'DELAY 1  t={elapsed}', None
    elif frame < n_encode_1_frames + n_delay_frames + n_encode_2_frames:
        return f'ENCODE 2  t={elapsed}', stim_input_2
    else:
        return f'DELAY 2  t={elapsed}', None

#def update(frame):
    phase_label, current_input = get_phase(frame)

    for step in range(steps_per_frame):
        field.step(current_input)

    img.set_data(field.u)

    spatial_output = np.sum(field.get_output(), axis=0)
    line_space.set_ydata(spatial_output)
    axes[1].set_ylim(-0.5, max(spatial_output.max() * 1.2, 1.0))

    color_output = np.sum(field.get_output(), axis=1)
    line_color.set_ydata(color_output)
    axes[2].set_ylim(-0.5, max(color_output.max() * 1.2, 1.0))

    time_text.set_text(phase_label)

    return img, line_space, line_color, time_text


def update(frame):
    phase_label, current_input = get_phase(frame)

    for step in range(steps_per_frame):
        field.step(current_input)

    img.set_data(field.u)

    spatial_max = np.max(field.u, axis=0)   # (200,)
    color_max   = np.max(field.u, axis=1)   # (50,)

    line_space.set_ydata(field.sigmoid(spatial_max))
    line_color.set_ydata(field.sigmoid(color_max))

    time_text.set_text(phase_label)

    return img, line_space, line_color, time_text


ani = FuncAnimation(fig, update, frames=n_total_frames, interval=30, blit=False)
#plt.show()

# Optional: save
ani.save('color_space_dft.mp4', writer='ffmpeg', fps=30, dpi=150)
