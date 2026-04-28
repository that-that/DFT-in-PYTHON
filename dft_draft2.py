import numpy as np
from scipy.ndimage import convolve1d
from scipy.ndimage import convolve

class DynamicField():
    def __init__(self, name, size, h=-5.0, tau = 80.0,
                 sigma_exc = 5.0, a_exc = 0.6,
                 sigma_inh = 10.0, a_inh= 0.3,
                 k_global = 0.0, beta = 4.0,
                 noise_std = 0.1, dt = 1.0, kernel_size = None):
        self.name = name
        self.dt = dt
        self.tau = tau
        self.h = h
        self.beta = beta
        self.noise_std = noise_std
        
        #1d vs 2d
        if isinstance(size, int):
            self.ndim = 1
            self.size = size
            self.u = np.full(size, h)
        else:
            self.ndim = 2
            self.size = size
            self.u = np.full(size, h)


        self.kernel = self.build_kernel(sigma_exc, a_exc, sigma_inh, a_inh, k_global, kernel_size = kernel_size)

        self.kernel_params = {
            'sigma_exc': sigma_exc, 'a_exc': a_exc,
            'sigma_inh': sigma_inh, 'a_inh': a_inh,
            'k_global': k_global
        }

        self.inputs = []

    def build_kernel (self, sigma_exc, a_exc, sigma_inh, a_inh, k_global, kernel_size=None):
        if self.ndim == 1:
            if kernel_size is not None:
                half = kernel_size //2
            else:
                half = self.size //2
            x = np.arange(-half, half + 1, dtype=float)
            kernel = (a_exc * np.exp(-x**2 / (2 * sigma_exc**2))
                      - a_inh * np.exp(-x**2 / (2 * sigma_inh**2))
                      - k_global)
            return kernel
        else:
            half_y, half_x = self.size[0]//2, self.size[1]//2
            y = np.arrange(-half_y, half_y+1, dtype=float)
            x = np.arrange(-half_x, half_x+1, dtype=float)
            Y, X = np.meshgrid(y, x, indexing = 'ij')
            r2 = X**2 + Y**2
            kernel = (a_exc * np.exp(-r2 / (2 * sigma_exc**2))
                      - a_inh * np.exp(-r2 / (2 * sigma_inh**2))
                      - k_global)
            return kernel
        

    def sigmoid(self, x):
        return 1.0 / (1.0 + np.exp(-self.beta *x)) #activation -> firing rate

    def convolution_method(self, activation):
        output = self.sigmoid(activation)
        if self.ndim == 1:
            return convolve1d(output, self.kernel, mode="wrap")
        else:
            return convolve(output, self.kernel, mode="wrap")
        

    def step(self, external_input=None):
        interaction = self.convolution_method(self.u)

        total_input = np.zeros_like(self.u)
        if external_input is not None:
            total_input += external_input

        for inp_func in self.inputs:
            total_input += inp_func()

        noise = self.noise_std * np.random.randn(*self.u.shape)

        du_dt = (-self.u + self.h + total_input + interaction + noise)/ self.tau
        self.u += self.dt * du_dt

        return self.u


    def reset(self):
        #reset field to a resting level
        if self.ndim ==1:
            self.u = np.full(self.size, self.h)
        else:
            self.u=np.full(self.size, self.h)

    def get_output(self):
        return self.sigmoid(self.u)

    def add_input(self, input_func):
        self.inputs.append(input_func)


    def set_resting_level(self, h):
        self.h = h


    def set_kernel_amplitudes(self, a_exc=None, a_inh=None):
        if a_exc is not None:
            self.kernel_params['a_exc'] = a_exc
        if a_inh is not None:
            self.kernel_params['a_inh'] = a_inh

        self.kernel = self.build_kernel(**self.kernel_params)
            

def gaussian_input(x, center, sigma, amplitude):
    return amplitude * np.exp(-(x - center)**2 / (2 * sigma**2))



