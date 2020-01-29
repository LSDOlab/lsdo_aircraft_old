import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types

from lsdo_aircraft.simple_rotor.simple_rotor_group import SimpleRotorGroup


class SimpleRotor(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleRotorGroup, values=[SimpleRotorGroup])

        self.declare('integrated_design_lift_coeff', default=0.3, types=float_types)
        self.declare('blade_solidity', default=0.15, types=float_types)

    def pre_setup(self):
        pass