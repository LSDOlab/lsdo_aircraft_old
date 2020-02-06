from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import constants, PowerCombinationComp


class SimpleTurbofanGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = ['sealevel_thrust']

    def setup(self):
        shape = self.options['shape']
        module = self.options['options_dictionary']

        comp = IndepVarComp()
        comp.add_output('throttle', shape=shape)
        comp.add_output('ref_3km_density', val=0.909122, shape=shape)
        comp.add_output('sealevel_density', val=1.225, shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        # comp = PowerCombinationComp(
        #     shape=shape,
        #     out_name='available_thrust',
        #     coeff=0.369,
        #     powers_dict=dict(
        #         sealevel_thrust=1.,
        #         mach_number=-0.305,
        #         density=1.,
        #         ref_3km_density=-1.,
        #     ),
        # )
        # self.add_subsystem('available_thrust_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='available_thrust',
            powers_dict=dict(
                mach_number=0.,
                sealevel_thrust=1.,
                density=1.,
                sealevel_density=-1.,
            ),
        )
        self.add_subsystem('available_thrust_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='thrust',
            powers_dict=dict(
                throttle=1.,
                available_thrust=1.,
            ),
        )
        self.add_subsystem('thrust_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='mass_flow_rate',
            coeff=module['thrust_specific_fuel_consumption'],
            powers_dict=dict(
                thrust=1.,
            ),
        )
        self.add_subsystem('mass_flow_rate_comp', comp, promotes=['*'])