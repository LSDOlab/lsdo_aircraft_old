from openmdao.api import Problem, Group
from motor_group import MotorGroup
import numpy as np

prob = Problem()
model = Group()
shape = 1
prob.model.add_subsystem('Motor', MotorGroup(shape=(1,), r4=0.1*np.ones(shape),
                                             P=50000*np.ones(shape), omega=700*np.ones(shape),
                                             t_env=293*np.ones(shape), tau_ti=550*10**6*np.ones(shape),
                                             t_max=433*np.ones(shape), rho_cu=8960*np.ones(shape),
                                             rho_fe=7874*np.ones(shape), rho_md=7010*np.ones(shape),
                                             rho_resistivity=1.68*10**-8*np.ones(shape), b_mg=0.9*np.ones(shape),
                                             a_m=8.5*10**4*np.ones(shape), eta_so=1.5*np.ones(shape),
                                             eta_ro=1.2*np.ones(shape), kw1=0.933*np.ones(shape),
                                             k_cu=386*np.ones(shape)), promotes=['*'])

prob.setup()
prob.run_model()


print('torque:', prob['torque'])
print('shaft_radius:', prob['shaft_radius'])
print('stator_thickness:', prob['stator_thickness'])
print('airgap_radius:', prob['airgap_radius'])
print('motor_length:', prob['motor_length'])
# print('t_increase:', prob['t_increase'])
print('stator_mass:', prob['stator_mass'])
# print('rotor_mass_temp_1:', prob['rotor_mass_temp_1'])
# print('rotor_mass_temp_2:', prob['rotor_mass_temp_2'])
# print('rotor_mass:', prob['rotor_mass'])
# print('shaft_mass:', prob['shaft_mass'])
print('total_mass:', prob['total_mass'])

print('iron loss:', prob['iron_loss'])
print('ohmic loss:', prob['ohmic_loss'])
print('efficiency:', prob['efficiency'])

print('torque available:', prob['torque_available'])

print('num poles:', prob['num_poles'])