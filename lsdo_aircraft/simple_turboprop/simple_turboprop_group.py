from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import constants, LinearPowerCombinationComp, PowerCombinationComp


class SimpleTurbopropGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = ['sealevel_power']

    def setup(self):
        shape = self.options['shape']
        module = self.options['options_dictionary']

        comp = IndepVarComp()
        comp.add_output('throttle', shape=shape)
        comp.add_output('sealevel_density', val=1.225, shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='available_power',
            powers_dict=dict(
                sealevel_power=1.,
                density=module['power_density_exponent'],
                sealevel_density=-module['power_density_exponent'],
            ),
        )
        self.add_subsystem('available_power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='power',
            powers_dict=dict(
                throttle=1.,
                available_power=1.,
            ),
        )
        self.add_subsystem('power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='mass_flow_rate',
            coeff=module['brake_specific_fuel_consumption'],
            powers_dict=dict(
                power=1.,
            ),
        )
        self.add_subsystem('mass_flow_rate_comp', comp, promotes=['*'])