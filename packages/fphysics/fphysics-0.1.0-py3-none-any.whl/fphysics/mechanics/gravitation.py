import numpy as np
from constants import *

G = GRAVITATIONAL_CONSTANT

def gravitational_force(m1, m2, r):
    return G * m1 * m2 / r**2

def gravitational_field(m, r):
    return G * m / r**2

def gravitational_potential_energy(m1, m2, r):
    return -G * m1 * m2 / r

def escape_velocity(m, r):
    return np.sqrt(2 * G * m / r)

def gravitational_potential(m, r):
    return -G * m / r

def orbital_velocity(m, r):
    return np.sqrt(G * m / r)

def period_of_orbit(m, r):
    return 2 * PI * np.sqrt(r**3 / (G * m))

def surface_gravity(m, r):
    return G * m / r**2
