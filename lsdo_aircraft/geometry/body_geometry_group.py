from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp


class BodyGeometryGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary', types=OptionsDictionary)

        self.promotes = None

    def setup(self):
        shape = self.options['shape']
        options_dictionary = self.options['options_dictionary']
        
        comp = IndepVarComp()
        comp.add_output('dummy_var')
        for name in [
            'wetted_area',
            'area',
            'characteristic_length',
        ]:
            comp.add_output(name, shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])