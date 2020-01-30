import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units, constants

from lsdo_aircraft.simple_reciprocating.simple_reciprocating_group import SimpleReciprocatingGroup


class SimpleReciprocating(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleReciprocatingGroup, values=[SimpleReciprocatingGroup])
        
        self.declare('brake_specific_fuel_consumption_lb_hph', default=0.3, types=float_types)

        self.declare('brake_specific_fuel_consumption', default=None, types=float_types, allow_none=True)

    def pre_setup(self):
        self['brake_specific_fuel_consumption'] = self['brake_specific_fuel_consumption_lb_hph'] / constants.W_hp * units('kg/W/s', 'lb/W/hr')