from __future__ import division, print_function
import numpy as np


def compute_Cf_lam(Re):
    Cf = 1.328 / Re ** 0.5 #Cf Laminar
    return Cf


def compute_Cf_lam_deriv(Re):
    dCf_dRe = -0.5 * 1.328 / Re ** 1.5
    return dCf_dRe


def compute_Cf_turb(Re, M=0.2): #Cf Turbulent
    # Cf = 0.417 / ( np.log(Re) / np.log(10) ) ** 2.58
    Cf = 0.455 / ( np.log(Re) / np.log(10) ) ** 2.58 / (1 + 0.144 * M ** 2) ** 0.65
    return Cf


def compute_Cf_turb_deriv(Re, M=0.2):
    # dCf_dRe = -2.58 * 0.417 / ( np.log(Re) / np.log(10) ) ** 3.58 * 1 / Re / np.log(10)
    dCf_dRe = -2.58 * 0.455 / ( np.log(Re) / np.log(10) ) ** 3.58 * 1 / Re / np.log(10) / (1 + 0.144 * M ** 2) ** 0.65
    return dCf_dRe


def compute_Cf_coefficients(Re_trans, delta_Re):
    Re_lam = Re_trans - delta_Re
    Re_turb = Re_trans + delta_Re

    Cf_lam = compute_Cf_lam(Re_lam) #Cf Laminar
    dCf_lam_dRe = compute_Cf_lam_deriv(Re_lam)
    Cf_turb = compute_Cf_turb(Re_turb) #Cf Turbulent
    dCf_turb_dRe = compute_Cf_turb_deriv(Re_turb)

    mtx = np.zeros((4, 4))
    mtx[0, :] = [Re_lam ** 3, Re_lam ** 2, Re_lam, 1.]
    mtx[1, :] = [Re_turb ** 3, Re_turb ** 2, Re_turb, 1.]
    mtx[2, :] = [3 * Re_lam ** 2, 2 * Re_lam, 1., 0.]
    mtx[3, :] = [3 * Re_turb ** 2, 2 * Re_turb, 1., 0.]

    rhs = np.zeros(4)
    rhs[:] = [Cf_lam, Cf_turb, dCf_lam_dRe, dCf_turb_dRe]

    sol = np.linalg.solve(mtx, rhs)
    a3, a2, a1, a0 = sol

    return a3, a2, a1, a0


def compute_Cf_trans(a3, a2, a1, a0, Re):
    Cf = Re ** 3 * a3 + Re ** 2 * a2 + Re * a1 + a0
    return Cf


def compute_Cf_trans_deriv(a3, a2, a1, a0, Re):
    dCf_dRe = 3 * Re ** 2 * a3 + 2 * Re * a2 + a1
    return dCf_dRe


def compute_Cf(a3, a2, a1, a0, Re_lam, Re_turb, Re):
    Cf = np.zeros(Re.shape)

    indices_lam = Re <= Re_lam
    indices_trans = np.logical_and(Re_lam <= Re, Re <= Re_turb)
    indices_turb = Re_turb <= Re

    Cf[indices_lam] = compute_Cf_lam(Re[indices_lam])
    Cf[indices_trans] = compute_Cf_trans(a3, a2, a1, a0, Re[indices_trans])
    Cf[indices_turb] = compute_Cf_turb(Re[indices_turb])

    return Cf


def compute_Cf_deriv(a3, a2, a1, a0, Re_lam, Re_turb, Re):
    dCf_dRe = np.zeros(Re.shape)

    indices_lam = Re <= Re_lam
    indices_trans = np.logical_and(Re_lam <= Re, Re <= Re_turb)
    indices_turb = Re_turb <= Re

    dCf_dRe[indices_lam] = compute_Cf_lam_deriv(Re[indices_lam])
    dCf_dRe[indices_trans] = compute_Cf_trans_deriv(a3, a2, a1, a0, Re[indices_trans])
    dCf_dRe[indices_turb] = compute_Cf_turb_deriv(Re[indices_turb])

    return dCf_dRe



if __name__ == '__main__':
    Re_trans = 5e5
    delta_Re = 20e4
    Re_lam = Re_trans - delta_Re
    Re_turb = Re_trans + delta_Re

    a3, a2, a1, a0 = compute_Cf_coefficients(Re_trans, delta_Re)

    print(a3, a2, a1, a0)


    import matplotlib.pyplot as plt

    n = 1001
    Re_list = np.linspace(0, 1e6, n)
    Cf_list = compute_Cf(a3, a2, a1, a0, Re_lam, Re_turb, Re_list)

    plt.plot(Re_list, Cf_list)
    plt.show()