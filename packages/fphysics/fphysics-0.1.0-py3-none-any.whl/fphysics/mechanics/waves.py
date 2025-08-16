import numpy as np
from constants import *

def wave_speed(wavelength, frequency):
    return wavelength * frequency

def wave_speed_string(T, mu):
    return np.sqrt(T / mu)

def wave_speed_gas(gamma, p, rho):
    return np.sqrt(gamma * p / rho)

def wave_speed_solid(E, rho):
    return np.sqrt(E / rho)

def wave_amplitude(y, k, x, omega, t):
    return y * np.sin(k * x - omega * t)

def wave_intensity(P, A):
    return P / A

def sound_intensity(p_rms, rho, v):
    return p_rms**2 / (rho * v)

def doppler_effect(f, v_source, v_observer, v_wave):
    return f * (v_wave + v_observer) / (v_wave - v_source)

def beat_frequency(f1, f2):
    return abs(f1 - f2)

def standing_wave_nodes(L, n):
    return n * L / 2

def standing_wave_antinodes(L, n):
    return (2 * n + 1) * L / 4

def interference_constructive(d, n, wavelength):
    return n * wavelength

def interference_destructive(d, n, wavelength):
    return (n + 0.5) * wavelength

def wave_power(A, omega, rho, v):
    return 0.5 * A**2 * omega**2 * rho * v

def wave_energy_density(A, omega, rho):
    return 0.5 * rho * A**2 * omega**2

def reflection_coefficient(Z1, Z2):
    return (Z1 - Z2) / (Z1 + Z2)

def transmission_coefficient(Z1, Z2):
    return 2 * Z1 / (Z1 + Z2)

def acoustic_impedance(rho, v):
    return rho * v

def decibel_level(I, I0=1e-12):
    return 10 * np.log10(I / I0)

def sound_pressure_level(p, p0=2e-5):
    return 20 * np.log10(p / p0)

def reverberation_time(V, A, c=343):
    return 0.161 * V / A

def absorption_coefficient(I_absorbed, I_incident):
    return I_absorbed / I_incident

def diffraction_single_slit(a, wavelength, theta):
    return np.sin(PI * a * np.sin(theta) / wavelength)

def diffraction_grating(d, n, wavelength):
    return n * wavelength / d

def fresnel_zone_radius(n, R, wavelength):
    return np.sqrt(n * R * wavelength)

def group_velocity(omega, k):
    return np.gradient(omega) / np.gradient(k)

def phase_velocity(omega, k):
    return omega / k

def dispersion_relation(omega, k, c):
    return omega - c * k

def wave_packet_width(delta_k):
    return 2 * PI / delta_k

def uncertainty_principle_waves(delta_x, delta_k):
    return delta_x * delta_k

def shock_wave_angle(v, c):
    return np.arcsin(c / v)

def mach_cone_angle(M):
    return np.arcsin(1 / M)

def sonic_boom_pressure(rho, v, c):
    return rho * v * c

def rayleigh_wave_speed(mu, rho, sigma):
    return np.sqrt(mu / rho) * np.sqrt(0.87 + 1.12 * sigma) / (1 + sigma)

def love_wave_speed(mu, rho, beta):
    return np.sqrt(mu / rho) * np.sqrt(1 - beta**2)
