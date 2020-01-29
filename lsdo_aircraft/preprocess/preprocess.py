import numpy as np

from lsdo_utils.api import OptionsDictionary

from lsdo_aircraft.preprocess.preprocess_group import PreprocessGroup


class Preprocess(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=PreprocessGroup, values=[PreprocessGroup])

    def pre_setup(self):
        pass