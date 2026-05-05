import numpy as np
import matplotlib.pyplot as plt

def generate_2d_gaussian(size, mu_x, mu_y, sigma_x, sigma_y):
    
    x = np.linspace(-5, 5, size)
    y = np.linspace(-5, 5, size)
    x, y = np.meshgrid(x, y)

    print(x, y)
    
    # basic 2D Gaussian formula
    z = (1 / (2 * np.pi * sigma_x * sigma_y) * 
         np.exp(-((x - mu_x)**2 / (2 * sigma_x**2) + (y - mu_y)**2 / (2 * sigma_y**2))))
    return x, y, z

x, y, z = generate_2d_gaussian(size=100, mu_x=0, mu_y=0, sigma_x=1.0, sigma_y=1.0)

#visual
plt.imshow(z, extent=[-5, 5, -5, 5])
plt.colorbar(label='Probability Density')
plt.title('2D Gaussian Distribution (Heatmap)')
plt.show()


