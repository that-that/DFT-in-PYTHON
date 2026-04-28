#dft draft 1
import numpy as np
import matplotlib.pyplot as plt 
from scipy.signal import convolve2d
from tqdm import tqdm
class DFT():
    def __init__(self, dt: float, total_time: float, neuron_pop : int, sigma_e, sigma_i, a_e, a_i, kernel_size = [5, 5]): #please make kernel size a list!!! [row, col]
        #set values
        self.dt = dt
        self.total_time_steps = np.arange(0, total_time, dt)

        self.u = np.zeros((neuron_pop, neuron_pop))
        self.input_val = np.zeros((neuron_pop, neuron_pop))

        self.sigma_e = sigma_e
        self.sigma_i = sigma_i



        self.x_array_template = np.linspace(-3*sigma_i, 3*sigma_i, kernel_size[0])
        self.y_array_template = np.linspace(-3*sigma_i, 3*sigma_i, kernel_size[1])

        self.x, self.y = np.meshgrid(self.x_array_template, self.y_array_template)

        self.kernel = a_e * np.e ** (-(self.x**2 + self.y**2)/(2*sigma_e**2)) - a_i * np.e ** (-(self.x**2 + self.y**2)/(2*sigma_i**2))

    #debug plot kernel
    def plot_kernel(self):
        plt.imshow(self.kernel)
        plt.colorbar()
        plt.show()

    def basic_2d_dft(self):
        self.input_val[25, 75] = 5
        self.input_val[75, 25] = 5

        self.u_per_time_step = []
        self.firing_rate_per_time_step = []

        for t in tqdm(self.total_time_steps, desc="simulating field"):
            current_firing_rates = 1/(1+np.exp(-self.u))
            lateral_interactions = convolve2d(current_firing_rates, self.kernel, mode='same')
            du = (-self.u + self.input_val + lateral_interactions) * self.dt
            self.u += du
            self.u_per_time_step.append(self.u.copy())
            self.firing_rate_per_time_step.append(1/(1+np.exp(-self.u)))


        plt.imshow(self.firing_rate_per_time_step[-1])
        plt.colorbar()
        return plt.show()



test = DFT(dt=0.001, total_time=1.0, neuron_pop=100, sigma_e=5, sigma_i=10, a_e=3, a_i=2, kernel_size=[11,11])

test.basic_2d_dft()
        
