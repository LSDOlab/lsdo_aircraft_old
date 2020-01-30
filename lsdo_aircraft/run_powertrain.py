from openmdao.api import Problem

from lsdo_aircraft.api import PowertrainGroup, Powertrain, Preprocess, Atmosphere, SimpleBattery, SimpleMotor, SimpleRotor


n = 250
shape = (n, n)

powertrain = Powertrain()

preprocess_name = 'preprocess'
atmosphere_name = 'atmosphere'
battery_name = 'battery'
motor_name = 'motor'
rotor_name = 'rotor'

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


prob = Problem()

prob.model = PowertrainGroup(
    shape=shape,
    powertrain=powertrain,
)
prob.setup(check=True)
prob.run_model()
# prob.model.list_outputs(print_arrays=True, prom_name=True)

import numpy as np
import matplotlib.pyplot as plt

torque_temp = np.linspace(0., 1., n)
angular_speed_temp = np.linspace(0., 600., n)




prob['motor_group.mass'] = 20
prob['motor_group.normalized_torque'] = np.tile(torque_temp, (n, 1))
prob['motor_group.angular_speed'] = np.tile(angular_speed_temp.T, (n, 1))
prob.run_model()
prob.model.list_outputs(print_arrays=True, prom_name=True)

plt.figure(1)
plt.scatter(
    prob['motor_group.angular_speed'],
    prob['motor_group.torque'],
)
plt.show()

plt.figure(2)
plt.scatter(
    prob['motor_group.angular_speed'],
    prob['motor_group.motor_efficiency'],
)
plt.show()

plt.figure(4)
plt.scatter(
    prob['motor_group.torque'],
    prob['motor_group.motor_efficiency'],
)
plt.show()


plt.figure(3)
plt.contour(
    [prob['motor_group.angular_speed'][0], prob['motor_group.torque'][:, 0], ],
    prob['motor_group.motor_efficiency'], levels=np.logspace(0, 100, 10)
)
plt.show()