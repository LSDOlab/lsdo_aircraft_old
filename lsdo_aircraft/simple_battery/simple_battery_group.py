from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import constants, LinearCombinationComp, PowerCombinationComp, ScalarExpansionComp


class SimpleBatteryGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']
        module = self.options['options_dictionary']

        comp = IndepVarComp()
        comp.add_output('mass_scalar')
        comp.add_output('normalized_power', shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        comp = ScalarExpansionComp(
            shape=shape,
            out_name='mass',
            in_name='mass_scalar',
        )
        self.add_subsystem('mass_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='weight',
            coeff=constants.g,
            powers_dict=dict(
                mass=1.,
            ),
        )
        self.add_subsystem('weight_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='usable_energy',
            coeff=module['specific_energy'] * (1 - module['reserve']),
            powers_dict=dict(
                mass=1.,
            ),
        )
        self.add_subsystem('usable_energy_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='maximum_power',
            coeff=module['specific_power'],
            powers_dict=dict(
                mass=1.,
            ),
        )
        self.add_subsystem('maximum_power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='power',
            powers_dict=dict(
                normalized_power=1.,
                maximum_power=1.,
            ),
        )
        self.add_subsystem('power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='energy',
            powers_dict=dict(
                power=1.,
                time=1.,
            ),
        )
        self.add_subsystem('energy_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='energy_constraint',
            coeffs_dict=dict(
                energy=1.,
                usable_energy=-1.,
            ),
        )
        self.add_subsystem('energy_constraint_comp', comp, promotes=['*'])