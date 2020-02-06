from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp


class LiftingSurfaceGeometryGroup(Group):

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
            'incidence_angle',
            'wetted_area',
            'area',
            'sweep',
            'aspect_ratio',
            'mac',
            'characteristic_length',
        ]:
            comp.add_output(name, shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])