from __future__ import division
import numpy as np

from lsdo_aircraft.atmosphere.constants import epsilon, h_trans
from lsdo_aircraft.atmosphere.constants import T0, T1, L, R
from lsdo_aircraft.atmosphere.constants import p0, p1, g, gamma


g_L_R = g / L / R

# tropopause
h_lower = h_trans - epsilon
h_upper = h_trans + epsilon
tropopause_matrix = np.array([
    [h_lower ** 3, h_lower ** 2, h_lower, 1],
    [h_upper ** 3, h_upper ** 2, h_upper, 1],
    [3 * h_lower ** 2, 2 * h_lower, 1, 0],
    [3 * h_upper ** 2, 2 * h_upper, 1, 0],
])

# pressure
tmp1 = 1 - L * h_lower / T0
tmp2 = np.exp(-g * epsilon / (R * T1))
pressure_rhs = np.array([
    p0 * tmp1 ** g_L_R,
    p1 * tmp2,
    (-p0 * g_L_R * (L / T0) * tmp1 ** (g_L_R - 1)),
    (p1 * -g / (R * T1) * tmp2)])
pressure_coeffs = np.linalg.solve(tropopause_matrix, pressure_rhs)

# temperature
temp_rhs = np.array([
    T0 - L * h_lower,
    T1,
    -L,
    0,
])
temp_coeffs = np.linalg.solve(tropopause_matrix, temp_rhs)

# functions
def get_mask_arrays(h_m):
    tropos_mask = h_m <= h_lower
    strato_mask = h_m >  h_upper
    smooth_mask = np.logical_and(~tropos_mask, ~strato_mask)
    return tropos_mask, strato_mask, smooth_mask

def compute_pressures(h_m, tropos_mask, strato_mask, smooth_mask):
    a, b, c, d = pressure_coeffs

    p_Pa = np.zeros(h_m.shape, dtype=h_m.dtype)
    p_Pa += tropos_mask * (p0 * (1 - L * h_m / T0) ** g_L_R)
    p_Pa += strato_mask * (p1 * np.exp(-g * (h_m - h_trans) / (R * T1)))
    p_Pa += smooth_mask * (a * h_m ** 3 + b * h_m ** 2 + c * h_m + d)

    return p_Pa

def compute_pressure_derivs(h_m, tropos_mask, strato_mask, smooth_mask):
    a, b, c, _ = pressure_coeffs

    derivs = np.zeros(h_m.shape, dtype=h_m.dtype)
    derivs += tropos_mask * (p0 * g_L_R * (-L / T0) * (1 - L * h_m / T0)** (g_L_R - 1))
    derivs += strato_mask * (p1 * (-g/(R * T1))
        *np.exp(g * h_trans / (R * T1)) * np.exp(-g * h_m / (R * T1)))
    derivs += smooth_mask * (3 * a * h_m ** 2 + 2 * b * h_m + c)

    return derivs

def compute_temps(h_m, tropos_mask, strato_mask, smooth_mask):
    a, b, c, d = temp_coeffs

    temp_K = np.zeros(h_m.shape, dtype=h_m.dtype)
    temp_K += tropos_mask * (T0 - L * h_m)
    temp_K += strato_mask * T1
    temp_K += smooth_mask * (a * h_m ** 3 + b * h_m ** 2 + c * h_m + d)

    return temp_K

def compute_temp_derivs(h_m, tropos_mask, strato_mask, smooth_mask):
    a, b, c, _ = temp_coeffs

    derivs = np.zeros(h_m.shape, dtype=h_m.dtype)
    derivs += tropos_mask * -L
    derivs += smooth_mask * (3 * a * h_m ** 2 + 2 * b * h_m + c)

    return derivs