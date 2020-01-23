from openmdao.api import Group, IndepVarComp, ExecComp

from lsdo_utils.api import PowerCombinationComp, LinearCombinationComp, LinearPowerCombinationComp, units

from lsdo_aircraft.sizing_performance.stall_wing_loading_comp import StallWingLoadingComp
from lsdo_aircraft.sizing_performance.maneuver_thrust_to_weight_comp import ClimbThrustToWeightComp
from lsdo_aircraft.sizing_performance.maneuver_thrust_to_weight_comp import TurnThrustToWeightComp
from lsdo_aircraft.sizing_performance.takeoff_wing_loading_comp import PropellerTakeoffWingLoadingComp
from lsdo_aircraft.sizing_performance.takeoff_wing_loading_comp import JetTakeoffWingLoadingComp
from lsdo_aircraft.sizing_performance.landing_wing_loading_comp import LandingWingLoadingComp


class SizingPerformanceGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft')

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']

        comp = IndepVarComp()
        comp.add_output('CL_max', val=aircraft['CL_max'], shape=shape)
        comp.add_output('CL_takeoff', val=aircraft['CL_takeoff'], shape=shape)
        comp.add_output('climb_gradient', val=aircraft['climb_gradient'], shape=shape)
        comp.add_output('turn_load_factor', val=aircraft['turn_load_factor'], shape=shape)
        comp.add_output('TOP', val=aircraft['TOP'], shape=shape)
        comp.add_output('takeoff_density', val=aircraft['takeoff_density'], shape=shape)
        comp.add_output('sealevel_density', val=1.225, shape=shape)
        comp.add_output('stall_speed', val=aircraft['stall_speed'], shape=shape)
        comp.add_output('climb_speed', val=aircraft['climb_speed'], shape=shape)
        comp.add_output('turn_speed', val=aircraft['turn_speed'], shape=shape)
        comp.add_output('landing_distance', val=aircraft['landing_distance'], shape=shape)
        comp.add_output('approach_distance', val=aircraft['approach_distance'], shape=shape)
        comp.add_output('wing_loading', val=aircraft['wing_loading'], shape=shape)
        comp.add_output('thrust_to_weight', val=aircraft['thrust_to_weight'], shape=shape)
        comp.add_output('ref_wing_loading', val=aircraft['ref_wing_loading'], shape=shape)
        comp.add_output('ref_thrust_to_weight', val=aircraft['ref_thrust_to_weight'], shape=shape)
        comp.add_design_var('wing_loading', indices=[0], lower=0.)
        comp.add_design_var('thrust_to_weight', indices=[0], lower=0.)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        #

        comp = PowerCombinationComp(
            shape=shape,
            out_name='wing_loading_lbf_ft2',
            powers_dict=dict(
                wing_loading=1.,
            ),
            coeff=units('lbf/ft^2', 'N/m^2'),
        )
        self.add_subsystem('wing_loading_lbf_ft2_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='ref_power_to_weight',
            powers_dict=dict(
                ref_thrust_to_weight=1.,
                cruise_speed=1.,
                propulsive_efficiency=-1.,
            ),
        )
        self.add_subsystem('ref_power_to_weight_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='power_to_weight',
            powers_dict=dict(
                thrust_to_weight=1.,
                cruise_speed=1.,
                propulsive_efficiency=-1.,
            ),
        )
        self.add_subsystem('power_to_weight_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='wing_area',
            powers_dict=dict(
                gross_weight=1.,
                wing_loading=-1.,
            ),
        )
        self.add_subsystem('wing_area_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='max_thrust',
            powers_dict=dict(
                gross_weight=1.,
                thrust_to_weight=1.,
            ),
        )
        self.add_subsystem('max_thrust_comp', comp, promotes=['*'])

        # 

        comp = StallWingLoadingComp(shape=shape)
        self.add_subsystem('stall_wing_loading_comp', comp, promotes=['*'])

        comp = ClimbThrustToWeightComp(shape=shape)
        self.add_subsystem('climb_thrust_to_weight_comp', comp, promotes=['*'])

        comp = TurnThrustToWeightComp(shape=shape)
        self.add_subsystem('turn_thrust_to_weight_comp', comp, promotes=['*'])

        if aircraft['thrust_source_type'] == 'jet':
            TakeoffWingLoadingComp = JetTakeoffWingLoadingComp
        elif aircraft['thrust_source_type'] == 'propeller':
            TakeoffWingLoadingComp = PropellerTakeoffWingLoadingComp
        else:
            raise Exception()

        comp = TakeoffWingLoadingComp(shape=shape)
        self.add_subsystem('takeoff_wing_loading_comp', comp, promotes=['*'])

        comp = LandingWingLoadingComp(shape=shape)
        self.add_subsystem('landing_wing_loading_comp', comp, promotes=['*'])

        # 
        for con_name in [
            'stall',
            'takeoff',
            'landing',
        ]:
            comp = LinearCombinationComp(
                shape=shape,
                out_name='{}_wing_loading_constraint'.format(con_name),
                coeffs_dict={
                    'wing_loading': 1.,
                    '{}_wing_loading'.format(con_name): -1.,
                },
            )
            comp.add_constraint('{}_wing_loading_constraint'.format(con_name), indices=[0], upper=0.)
            self.add_subsystem('{}_wing_loading_constraint_comp'.format(con_name), comp, promotes=['*'])

        for con_name in [
            'climb',
            'turn',
        ]:
            comp = LinearCombinationComp(
                shape=shape,
                out_name='{}_thrust_to_weight_constraint'.format(con_name),
                coeffs_dict={
                    'thrust_to_weight': -1.,
                    '{}_thrust_to_weight'.format(con_name): 1.,
                },
            )
            comp.add_constraint('{}_thrust_to_weight_constraint'.format(con_name), indices=[0], upper=0.)
            self.add_subsystem('{}_thrust_to_weight_constraint_comp'.format(con_name), comp, promotes=['*'])

            comp = PowerCombinationComp(
                shape=shape,
                out_name='{}_power_to_weight'.format(con_name),
                powers_dict={
                    '{}_thrust_to_weight'.format(con_name): 1.,
                    'cruise_speed': 1.,
                    'propulsive_efficiency': -1.,
                },
            )
            self.add_subsystem('{}_power_to_weight_comp'.format(con_name), comp, promotes=['*'])

        a = 0.5
        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='sizing_performance_objective',
            terms_list=[
                (1 - a, dict(
                    thrust_to_weight=1.,
                    ref_thrust_to_weight=-1.,
                )),
                (-a, dict(
                    wing_loading=1.,
                    ref_wing_loading=-1.,
                )),
            ],
        )
        self.add_subsystem('sizing_performance_objective_comp'.format(con_name), comp, promotes=['*'])