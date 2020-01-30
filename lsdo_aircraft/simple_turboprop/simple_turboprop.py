import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units, constants

from lsdo_aircraft.simple_turboprop.simple_turboprop_group import SimpleTurbopropGroup


class SimpleTurboprop(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleTurbopropGroup, values=[SimpleTurbopropGroup])
        
        self.declare('brake_specific_fuel_consumption_lb_hph', default=0.65, types=float_types)
        self.declare('power_density_exponent', default=0.7, types=float_types)

        self.declare('brake_specific_fuel_consumption', default=None, types=float_types, allow_none=True)

    def pre_setup(self):
        self['brake_specific_fuel_consumption'] = self['brake_specific_fuel_consumption_lb_hph'] / constants.W_hp * units('kg/W/s', 'lb/W/hr')