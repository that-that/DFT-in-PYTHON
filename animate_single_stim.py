from quad_dft_model import QuadTaskModel
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

model = QuadTaskModel()

stim = model.make_stimulus("red_square_left", 20.0, 20.0, 40.0, (100, 200, 100))

steps_per_frame = 10
n_encode_frames = 200
n_delay_frames = 200
n_total = n_encode_frames + n_delay_frames

fig, axes = plt.subplots(3, 2, figsize=(14, 10))
fig.suptitle('Quad Task Model — Red Square on the Left', fontsize=14)

img_cs = axes[0, 0].imshow(model.color_space.u, aspect='auto', cmap='RdBu_r',
                           vmin=-8, vmax=15, origin='lower')
axes[0, 0].set_title('Color x Space')
axes[0, 0].set_xlabel('Space')
axes[0, 0].set_ylabel('Color')
fig.colorbar(img_cs, ax=axes[0, 0])

img_ss = axes[0, 1].imshow(model.shape_space.u, aspect='auto', cmap='RdBu_r',
                           vmin=-8, vmax=15, origin='lower')
axes[0, 1].set_title('Shape x Space')
axes[0, 1].set_xlabel('Space')
axes[0, 1].set_ylabel('Shape')
fig.colorbar(img_ss, ax=axes[0, 1])

x_space = np.arange(200)
line_swm, = axes[1, 0].plot(x_space, model.spatial_wm.u, 'b-', lw=2)
axes[1, 0].set_ylim(-8, 15)
axes[1, 0].set_title('Spatial WM')
axes[1, 0].set_xlabel('Position')
axes[1, 0].set_ylabel('Activation')
axes[1, 0].axhline(y=0, color='gray', ls='--', alpha=0.5)
axes[1, 0].axvline(x=0, color='green', ls=':', alpha=0.5, label='Left (0)')
axes[1, 0].legend()

line_stim, = axes[1, 1].plot(x_space, stim['spatial'], 'g-', lw=2)
axes[1, 1].set_ylim(-1, 10)
axes[1, 1].set_title('External Spatial Input')
axes[1, 1].set_xlabel('Position')
axes[1, 1].axvline(x=0, color='green', ls=':', alpha=0.5, label='Left (0)')
axes[1, 1].legend()

x_color = np.arange(100)
line_color, = axes[2, 0].plot(x_color, model.color_attn.u, 'r-', lw=2)
axes[2, 0].set_ylim(-10, 10)
axes[2, 0].set_title('Color Attention')
axes[2, 0].set_xlabel('Color')
axes[2, 0].axhline(y=0, color='gray', ls='--', alpha=0.5)
axes[2, 0].axvline(x=0, color='red', ls=':', alpha=0.5, label='Red (0)')
axes[2, 0].legend()

x_shape = np.arange(100)
line_shape, = axes[2, 1].plot(x_shape, model.shape_attn.u, 'r-', lw=2)
axes[2, 1].set_ylim(-10, 10)
axes[2, 1].set_title('Shape Attention')
axes[2, 1].set_xlabel('Shape')
axes[2, 1].axhline(y=0, color='gray', ls='--', alpha=0.5)
axes[2, 1].axvline(x=0, color='purple', ls=':', alpha=0.5, label='Square (0)')
axes[2, 1].legend()

time_text = axes[0, 0].text(0.02, 0.95, '', transform=axes[0, 0].transAxes,
                            fontsize=12, fontweight='bold',
                            verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()

def get_phase(frame):
    elapsed = frame * steps_per_frame
    if frame < n_encode_frames:
        return f'ENCODING  t={elapsed}ms', stim
    else:
        return f'DELAY  t={elapsed}ms', None

def update(frame):
    phase_label, current_stim = get_phase(frame)

    for _ in range(steps_per_frame):
        model.step(current_stim)

    img_cs.set_data(model.color_space.u)
    img_ss.set_data(model.shape_space.u)

    line_swm.set_ydata(model.spatial_wm.u)
    line_color.set_ydata(model.color_attn.u)
    line_shape.set_ydata(model.shape_attn.u)

    if current_stim is not None:
        line_stim.set_ydata(current_stim['spatial'])
    else:
        line_stim.set_ydata(np.zeros(200))

    time_text.set_text(phase_label)

    return img_cs, img_ss, line_swm, line_stim, line_color, line_shape, time_text

ani = FuncAnimation(fig, update, frames=n_total, interval=30, blit=False, repeat=False)
plt.show()
