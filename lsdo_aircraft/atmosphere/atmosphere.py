import numpy as np

from lsdo_utils.api import OptionsDictionary

from lsdo_aircraft.atmosphere.atmosphere_group import AtmosphereGroup


class Atmosphere(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=AtmosphereGroup, values=[AtmosphereGroup])

    def pre_setup(self):
        pass