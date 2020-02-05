import numpy as np
from openmdao.api import Group, IndepVarComp

from lsdo_aircraft.aerodynamics.reynolds_comp import \
    ReynoldsComp
from lsdo_utils.comps.arithmetic_comps.linear_combination_comp import \
    LinearCombinationComp
from lsdo_utils.comps.arithmetic_comps.power_combination_comp import \
    PowerCombinationComp
from lsdo_utils.comps.arithmetic_comps.ks_comp import \
    KSComp
from lsdo_utils.comps.array_comps.array_reshape_comp import \
    ArrayReshapeComp
from lsdo_utils.comps.array_comps.scalar_expansion_comp import \
    ScalarExpansionComp
from lsdo_aircraft.aerodynamics.force_coeff_comp import ForceCoeffComp
from lsdo_aircraft.aerodynamics.force_comp import ForceComp
from lsdo_aircraft.aerodynamics.induced_drag_coeff_comp import \
    InducedDragCoeffComp
from lsdo_aircraft.aerodynamics.lift_coeff_comp import LiftCoeffComp
from lsdo_aircraft.aerodynamics.lift_curve_slope_comp import LiftCurveSlopeComp
from lsdo_aircraft.aerodynamics.lift_curve_slope_tmp_comp import \
    LiftCurveSlopeTmpComp
from lsdo_aircraft.aerodynamics.lifting_surface_ff_comp import \
    LiftingSurfaceFFComp
from lsdo_aircraft.aerodynamics.oswald_efficiency_comp import OswaldEfficiencyComp
from lsdo_aircraft.aerodynamics.parasitic_drag_coeff_comp import \
    ParasiticDragCoeffComp
from lsdo_aircraft.aerodynamics.skin_friction_coeff_comp import \
    SkinFrictionCoeffComp
from lsdo_aircraft.geometry.body import Body
from lsdo_aircraft.aerodynamics.dynamic_pressure_comp import DynamicPressureComp

# from lsdo_utils.api import OptionsDictionary, float_types, units
from lsdo_utils.api import float_types

from lsdo_utils.comps.arithmetic_comps.scaling_comp import ScalingComp

from lsdo_aircraft.weights.wing_weight_comp import WingWeightComp
from lsdo_aircraft.weights.htail_weight_comp import HTailWeightComp
from lsdo_aircraft.weights.motor_weight_comp import MotorWeightComp
from lsdo_aircraft.weights.cg_comp import CGComp
from lsdo_aircraft.weights.max_2_comp import Max2Comp
from lsdo_aircraft.api import Rotor, LiftingSurface, NonliftingSurface

from lsdo_aircraft.api import (AerodynamicsGroup, DynamicPressureComp,
                               ForceCoeffComp, ForceComp, LiftCoeffComp,
                               LiftCurveSlopeComp, LiftingSurfaceFFComp,
                               OswaldEfficiencyComp, ParasiticDragCoeffComp,
                               ReynoldsComp, SkinFrictionCoeffComp, Body,
                               LiftingSurface, NonliftingSurface, Rotor,
                               WeightsGroup, AtmosphereGroup, GeometryGroup)


class AnalysisGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Body)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        atmos = AtmosphereGroup(shape=shape, module=None)
        geom = GeometryGroup(shape=shape, aircraft=aircraft)
        aero = AerodynamicsGroup(shape=shape, aircraft=aircraft)
        weights = WeightsGroup(shape=shape, aircraft=aircraft)
        self.add_subsystem('atmos', atmos, promotes=['*'])
        self.add_subsystem('geom', geom, promotes=['*'])
        self.add_subsystem('aero', aero, promotes=['*'])
        self.add_subsystem('weights', weights, promotes=['*'])
        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            self.connect(
                '{}_weights_group.weight'.format(name),
                '{}_weight'.format(name),
            )
            self.connect(
                '{}_area'.format(name),
                '{}_weights_group.area'.format(name),
            )
            self.connect(
                '{}_aspect_ratio'.format(name),
                '{}_weights_group.aspect_ratio'.format(name),
            )
            self.connect(
                '{}_sweep_deg'.format(name),
                '{}_weights_group.sweep_deg'.format(name),
            )
            self.connect(
                '{}_sweep_deg'.format(name),
                '{}_aerodynamics_group.sweep'.format(name),
            )
            self.connect(
                '{}_taper_ratio'.format(name),
                '{}_weights_group.taper_ratio'.format(name),
            )
            self.connect(
                '{}_t_c'.format(name),
                '{}_aerodynamics_group.t_c'.format(name),
            )
        for nonlifting_surface in aircraft['nonlifting_surfaces']:
            name = nonlifting_surface['name']
            self.connect(
                '{}_weights_group.weight'.format(name),
                '{}_weight'.format(name),
            )
