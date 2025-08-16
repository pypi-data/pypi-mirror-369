import numpy as np
from constants import *

def pressure_depth(rho, h):
    return rho * EARTH_GRAVITY * h

def buoyant_force(rho, V):
    return rho * EARTH_GRAVITY * V

def reynolds_number(rho, v, L, mu):
    return rho * v * L / mu

def drag_force(rho, v, A, Cd):
    return 0.5 * rho * v**2 * A * Cd

def lift_force(rho, v, A, Cl):
    return 0.5 * rho * v**2 * A * Cl

def bernoulli_equation(p1, v1, h1, p2, v2, h2, rho):
    return p1 + 0.5 * rho * v1**2 + rho * EARTH_GRAVITY * h1 - (p2 + 0.5 * rho * v2**2 + rho * EARTH_GRAVITY * h2)

def continuity_equation(A1, v1, A2, v2):
    return A1 * v1 - A2 * v2

def torricelli_law(h):
    return np.sqrt(2 * EARTH_GRAVITY * h)

def viscous_force(eta, A, dv_dy):
    return eta * A * dv_dy

def stokes_drag(eta, r, v):
    return 6 * PI * eta * r * v

def poiseuille_flow(delta_p, r, L, eta):
    return PI * delta_p * r**4 / (8 * eta * L)

def flow_rate(A, v):
    return A * v

def dynamic_pressure(rho, v):
    return 0.5 * rho * v**2

def static_pressure(rho, h):
    return rho * EARTH_GRAVITY * h

def hydrostatic_pressure(p0, rho, h):
    return p0 + rho * EARTH_GRAVITY * h

def archimedes_principle(rho_fluid, V_submerged):
    return rho_fluid * EARTH_GRAVITY * V_submerged

def surface_tension_force(gamma, L):
    return gamma * L

def capillary_rise(gamma, theta, rho, r):
    return 2 * gamma * np.cos(theta) / (rho * EARTH_GRAVITY * r)

def weber_number(rho, v, L, gamma):
    return rho * v**2 * L / gamma

def froude_number(v, L):
    return v / np.sqrt(EARTH_GRAVITY * L)

def mach_number(v, c):
    return v / c

def compressibility(dp, dV, V):
    return -dV / (V * dp)

def bulk_modulus(dp, dV, V):
    return -dp * V / dV

def shear_modulus(tau, gamma):
    return tau / gamma

def kinematic_viscosity(eta, rho):
    return eta / rho

def prandtl_number(mu, cp, k):
    return mu * cp / k

def peclet_number(v, L, alpha):
    return v * L / alpha

def grashof_number(g, beta, T, L, nu):
    return g * beta * T * L**3 / nu**2

def rayleigh_number(g, beta, T, L, nu, alpha):
    return g * beta * T * L**3 / (nu * alpha)

def nusselt_number(h, L, k):
    return h * L / k
