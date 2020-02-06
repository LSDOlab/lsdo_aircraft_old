from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import constants, LinearCombinationComp, PowerCombinationComp, ScalarExpansionComp, ElementwiseMinComp

import numpy as np

class SimpleMotorGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']
        module = self.options['options_dictionary']


        comp = IndepVarComp()
        comp.add_output('mass', shape=shape)
        comp.add_output('normalized_torque', shape=shape)
        comp.add_output('angular_speed', shape=shape)
        for var_name in [
            'magnetic_flux_density',
            'line_current_density',
            'number_of_poles_per_phase',
            'hysteresis_coeff',
            'copper_resistivity',
            'eta_slot',
            'eta_fill',
        ]:
            comp.add_output(var_name, val=module[var_name], shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='supply_frequency',
            coeff=(60 / (2 * np.pi)) * (1/120),
            powers_dict=dict(
                number_of_poles_per_phase=1.,
                angular_speed=1.,
            ),
        )
        self.add_subsystem('supply_frequency_comp', comp, promotes=['*'])

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
            rho=1.e-1,
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
            out_name='mass_stator',
            coeff=0.53,
            powers_dict=dict(
                mass=1.
            ),

        )
        self.add_subsystem('mass_stator_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='mass_rotor',
            coeff=0.47,
            powers_dict=dict(
                mass=1.
            ),
        )
        self.add_subsystem('mass_rotor_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='outer_diameter',
            coeff=96.9,
            powers_dict=dict(
                mass=0.344,
            ),
        )
        self.add_subsystem('outer_diameter_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='motor_length',
            coeff=0.35,
            powers_dict=dict(
                outer_diameter=1.,
            ),
        )
        self.add_subsystem('motor_length_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='stator_diameter',
            coeff=0.5,
            powers_dict=dict(
                outer_diameter=1.,
            ),
        )
        self.add_subsystem('stator_diameter_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='shaft_diameter',
            coeff=0.085,
            powers_dict=dict(
                outer_diameter=1.,
            ),
        )
        self.add_subsystem('shaft_diameter_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='stator_thickness',
            coeffs_dict=dict(
                stator_diameter=.5,
                shaft_diameter=-.5
            ),
        )
        self.add_subsystem('stator_thickness_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='eddy_loss',
            coeff=1.1 * (1/50)**1.5,
            powers_dict=dict(
                supply_frequency=1.5,
                mass_stator=1.,
                magnetic_flux_density=2.,
            ),
        )
        self.add_subsystem('eddy_loss_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='hysteresis_loss',
            powers_dict=dict(
                supply_frequency=1.,
                mass_rotor=1.,
                magnetic_flux_density=2.,
                hysteresis_coeff=1.
            ),
        )
        self.add_subsystem('hysteresis_loss_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='iron_loss',
            coeffs_dict=dict(
                hysteresis_loss=1.,
                eddy_loss=1.
            ),
        )
        self.add_subsystem('iron_loss_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='heat_loss_nominal',
            coeff=0.5,
            powers_dict=dict(
                shaft_diameter=1.,
                motor_length=1.,
                copper_resistivity=1.,
                line_current_density=2.,
                eta_slot=-1.,
                eta_fill=-1.,
                stator_thickness=-1.
            ),
        )
        self.add_subsystem('heat_loss_nominal_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='heat_loss',
            powers_dict=dict(
                heat_loss_nominal=1.,
                normalized_torque=2.
            ),
        )
        self.add_subsystem('heat_loss_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='input_power',
            coeffs_dict=dict(
                shaft_power=1.,
                iron_loss=1.,
                heat_loss=1.
            ),
        )
        self.add_subsystem('input_power_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='motor_efficiency',
            coeff=100,
            powers_dict=dict(
                shaft_power=1.,
                input_power=-1.,
            ),
        )
        self.add_subsystem('motor_efficiency_comp', comp, promotes=['*'])




