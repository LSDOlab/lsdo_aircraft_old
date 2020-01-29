from openmdao.api import Problem

from lsdo_aircraft.api import PowertrainGroup, Powertrain, Preprocess, Atmosphere, SimpleBattery, SimpleMotor, SimpleRotor


shape = (1,)

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
prob.model.list_outputs()