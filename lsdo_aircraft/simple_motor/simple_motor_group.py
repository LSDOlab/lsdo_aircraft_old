from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import constants, LinearCombinationComp, PowerCombinationComp, ScalarExpansionComp, ElementwiseMinComp


class SimpleMotorGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('module')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']
        module = self.options['module']

        comp = IndepVarComp()
        comp.add_output('mass', shape=shape)
        comp.add_output('normalized_torque', shape=shape)
        comp.add_output('angular_speed', shape=shape)
        comp.add_output('efficiency', val=0.9, shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='continuous_torque',
            coeff=module['torque_mass_coeff'],
            powers_dict=dict(
                mass=module['torque_mass_power'],
            ),
        )
        self.add_subsystem('continuous_torque_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='continuous_power',
            coeff=module['specific_power'],
            powers_dict=dict(
                mass=1.,
            ),
        )
        self.add_subsystem('continuous_power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='flux_weakening_torque',
            powers_dict=dict(
                continuous_power=1.,
                angular_speed=-1.,
            ),
        )
        self.add_subsystem('flux_weakening_torque_comp', comp, promotes=['*'])

        comp = ElementwiseMinComp(
            shape=shape,
            out_name='available_torque',
            in_names=['continuous_torque', 'flux_weakening_torque'],
            rho=20.,
        )
        self.add_subsystem('available_torque_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='torque',
            powers_dict=dict(
                normalized_torque=1.,
                available_torque=1.,
            ),
        )
        self.add_subsystem('torque_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='shaft_power',
            powers_dict=dict(
                torque=1.,
                angular_speed=1.,
            ),
        )
        self.add_subsystem('shaft_power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='electric_power',
            powers_dict=dict(
                shaft_power=1.,
                efficiency=-1.,
            ),
        )
        self.add_subsystem('electric_power_comp', comp, promotes=['*'])