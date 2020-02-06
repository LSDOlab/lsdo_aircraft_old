from __future__ import print_function

from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import PowerCombinationComp


class PreprocessGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']

        comp = IndepVarComp()
        comp.add_output('altitude', shape=shape)
        comp.add_output('speed', shape=shape)
        comp.add_output('distance', shape=shape)
        comp.add_output('time', shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])