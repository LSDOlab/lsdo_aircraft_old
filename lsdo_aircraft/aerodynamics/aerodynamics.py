import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants

from lsdo_aircraft.aerodynamics.aerodynamics_group import AerodynamicsGroup


float_array_types = (int, float, np.ndarray)

class Aerodynamics(OptionsDictionary):

    def initialize(self):
        self.declare('name', default='aerodynamics', types=str)
        self.declare('group_class', default=AerodynamicsGroup, values=[AerodynamicsGroup])