import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units

from lsdo_aircraft.simple_turbofan.simple_turbofan_group import SimpleTurbofanGroup


class SimpleTurbofan(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleTurbofanGroup, values=[SimpleTurbofanGroup])
        
        self.declare('thrust_specific_fuel_consumption_lb_lbfh', default=0.61, types=float_types)

        self.declare('thrust_specific_fuel_consumption', default=None, types=float_types, allow_none=True)

    def pre_setup(self):
        self['thrust_specific_fuel_consumption'] = self['thrust_specific_fuel_consumption_lb_lbfh'] * units('kg/N/s', 'lb/lbf/hr')