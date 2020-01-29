import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units

from lsdo_aircraft.simple_motor.simple_motor_group import SimpleMotorGroup


class SimpleMotor(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleMotorGroup, values=[SimpleMotorGroup])
        
        self.declare('specific_power_kW_kg', default=5., types=float_types)
        self.declare('torque_mass_coeff', default=2.8, types=float_types)
        self.declare('torque_mass_power', default=1.5, types=float_types)

        self.declare('specific_power', default=None, types=float_types, allow_none=True)

    def pre_setup(self):
        self['specific_power'] = self['specific_power_kW_kg'] * units('W/kg', 'kW/kg')