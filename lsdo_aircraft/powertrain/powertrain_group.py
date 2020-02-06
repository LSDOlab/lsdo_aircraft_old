from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import LinearCombinationComp, PowerCombinationComp, constants


class PowertrainGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('powertrain')
        
    def setup(self):
        shape = self.options['shape']
        powertrain = self.options['powertrain']

        for module in powertrain.modules:
            name = module['name']
            group_class = module['group_class']

            group = group_class(shape=shape, options_dictionary=module)
            self.add_subsystem('{}_group'.format(name), group, promotes=group.promotes)

        for src_name, src_var_names, tgt_name, tgt_var_names in powertrain.links:
            for src_var_name, tgt_var_name in zip(src_var_names, tgt_var_names):
                self.connect(
                    '{}_group.{}'.format(src_name, src_var_name),
                    '{}_group.{}'.format(tgt_name, tgt_var_name),
                )