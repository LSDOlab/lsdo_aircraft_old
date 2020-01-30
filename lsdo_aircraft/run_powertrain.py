from openmdao.api import Problem, IndepVarComp

from lsdo_aircraft.api import PowertrainGroup, Powertrain, Preprocess, Atmosphere
from lsdo_aircraft.api import SimpleBattery, SimpleMotor, SimpleRotor, SimpleReciprocating, SimpleTurbofan, SimpleTurboprop


n = 100
shape = (n, n)

powertrain = Powertrain()

preprocess_name = 'preprocess'
atmosphere_name = 'atmosphere'
battery_name = 'battery'
motor_name = 'motor'
rotor_name = 'rotor'
reciprocating_name = 'reciprocating'
turbofan_name = 'turbofan'
turboprop_name = 'turboprop'

powertrain.add_module(Preprocess(
    name=preprocess_name,
))
powertrain.add_module(Atmosphere(
    name=atmosphere_name,
))
powertrain.add_module(SimpleBattery(
    name=battery_name,
))
powertrain.add_module(SimpleMotor(
    name=motor_name,
))
powertrain.add_module(SimpleRotor(
    name=rotor_name,
))
powertrain.add_module(SimpleReciprocating(
    name=reciprocating_name,
))
powertrain.add_module(SimpleTurbofan(
    name=turbofan_name,
))
powertrain.add_module(SimpleTurboprop(
    name=turboprop_name,
))

powertrain.add_link(
    preprocess_name, 'altitude',
    atmosphere_name, 'altitude',
)
powertrain.add_link(
    preprocess_name, 'speed',
    atmosphere_name, 'speed',
)
powertrain.add_link(
    preprocess_name, 'time',
    battery_name, 'time',
)
powertrain.add_link(
    motor_name, ['angular_speed', 'shaft_power'],
    rotor_name, ['angular_speed', 'shaft_power'],
)
powertrain.add_link(
    preprocess_name, 'speed',
    rotor_name, 'speed',
)
powertrain.add_link(
    atmosphere_name, ['density', 'sonic_speed'],
    rotor_name, ['density', 'sonic_speed'],
)
powertrain.add_link(
    atmosphere_name, ['density'],
    reciprocating_name, ['density'],
)
powertrain.add_link(
    atmosphere_name, ['density', 'mach_number'],
    turbofan_name, ['density', 'mach_number'],
)
powertrain.add_link(
    atmosphere_name, ['density'],
    turboprop_name, ['density'],
)


prob = Problem()

comp = IndepVarComp()
comp.add_output('sealevel_power', val=200.e3, shape=shape)
comp.add_output('sealevel_thrust', val=200.e3, shape=shape)
prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

group = PowertrainGroup(
    shape=shape,
    powertrain=powertrain,
)
prob.model.add_subsystem('group', group, promotes=['*'])
prob.setup(check=True)
# prob.run_model()
# prob.model.list_outputs(print_arrays=True, prom_name=True)

import numpy as np
import matplotlib.pyplot as plt

torque_temp = np.linspace(0., 1., n)
angular_speed_temp = np.linspace(0., 600., n)


prob['motor_group.mass'] = 20.


prob['motor_group.normalized_torque'] = np.outer(
    np.linspace(0, 1., n),
    np.ones(n),
)
prob['motor_group.angular_speed'] = np.outer(
    np.ones(n),
    np.linspace(0, 600., n),
)

prob.run_model()
# prob.model.list_outputs(print_arrays=True, prom_name=True)


low = 50.
high = 92.8
levels = high - np.linspace(0., 1., 15) ** 3. * (high - low)
levels = [np.round(val, 3) for val in levels]
levels = levels[::-1]

low = 0.
high = 100.
levelsf = high - np.linspace(0., 1., 100) ** 3. * (high - low)
levelsf = levelsf[::-1]

plt.figure()
plt.contourf(
    prob['motor_group.angular_speed'] * 60. / 2. / np.pi, prob['motor_group.torque'],
    prob['motor_group.motor_efficiency'], 
    levels=levelsf,
)
cs = plt.contour(
    prob['motor_group.angular_speed'] * 60. / 2. / np.pi, prob['motor_group.torque'],
    prob['motor_group.motor_efficiency'], colors='k',
    levels=levels,
)
plt.plot(
    prob['motor_group.angular_speed'][0, :] * 60. / 2. / np.pi,
    prob['motor_group.available_torque'][0, :],
    'k'
)
if plt.rcParams["text.usetex"]:
    fmt = r'%r \%%'
else:
    fmt = '%r %%'
plt.clabel(cs, inline=True, fmt=fmt, fontsize=10)
plt.ylim([0., 600.])
plt.xlabel(r'Rotational speed [RPM]')
plt.ylabel(r'Torque [Nm]')
plt.show()
