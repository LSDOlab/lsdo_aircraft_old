import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants


float_array_types = (int, float, np.ndarray)

class Geometry(OptionsDictionary):

    def initialize(self):
        pass

    def pre_setup(self):
        pass