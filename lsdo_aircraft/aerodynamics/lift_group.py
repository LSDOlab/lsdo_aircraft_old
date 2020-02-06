import numpy as np

from openmdao.api import Group

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, GeneralOperationComp, LinearPowerCombinationComp

from lsdo_aircraft.aerodynamics.lift_curve_slope_denominator_comp import LiftCurveSlopeDenominatorComp


class LiftGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('part', types=OptionsDictionary)

    def setup(self):
        shape = self.options['shape']
        part = self.options['part']

        lift_coeff_zero_alpha = part['lift_coeff_zero_alpha']
        lift_curve_slope_2D = part['lift_curve_slope_2D']
        dynamic_pressure_ratio = part['dynamic_pressure_ratio']
        downwash_slope = part['downwash_slope']
        wing_exposed_ratio = part['wing_exposed_ratio']
        fuselage_diameter_span = part['fuselage_diameter_span']
            
        comp = LiftCurveSlopeDenominatorComp(
            shape=shape,
            lift_curve_slope_2D=lift_curve_slope_2D,
            wing_exposed_ratio=wing_exposed_ratio,
            fuselage_diameter_span=fuselage_diameter_span,
        )
        self.add_subsystem('lift_curve_slope_denominator_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='lift_curve_slope',
            coeff=2 * np.pi * wing_exposed_ratio * 1.07 * (1. + fuselage_diameter_span) ** 2.,
            powers_dict=dict(
                aspect_ratio=1.,
                lift_curve_slope_denominator=-1.,
            ),
        )
        self.add_subsystem('lift_curve_slope_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='lift_curve_slope_modified',
            coeffs_dict=dict(
                lift_curve_slope=(1 - downwash_slope) * dynamic_pressure_ratio,
            )
        )
        self.add_subsystem('lift_curve_slope_modified_comp', comp, promotes=['*'])

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='lift_coeff',
            constant=dynamic_pressure_ratio * lift_coeff_zero_alpha,
            terms_list=[
                (dynamic_pressure_ratio * (1 - downwash_slope), dict(
                    lift_curve_slope=1.,
                    alpha=1.,
                )),
                (dynamic_pressure_ratio, dict(
                    lift_curve_slope=1.,
                    incidence_angle=1.,
                )),
            ],
        )
        self.add_subsystem('lift_coeff_comp', comp, promotes=['*'])