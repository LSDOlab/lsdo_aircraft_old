import numpy as np
from openmdao.api import Group, IndepVarComp

from lsdo_aircraft.aerodynamics.reynolds_comp import \
    ReynoldsComp
from lsdo_utils.comps.arithmetic_comps.linear_combination_comp import \
    LinearCombinationComp
from lsdo_utils.comps.arithmetic_comps.power_combination_comp import \
    PowerCombinationComp
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

# from lsdo_utils.api import OptionsDictionary, float_types, units
from lsdo_utils.api import float_types


class AerodynamicsGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Body)
        self.options.declare('incidence_angle', default=0., types=float_types)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        incidence_angle = self.options['incidence_angle']

        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            mirror = lifting_surface['mirror']
            reference = lifting_surface['reference']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            group = Group()

            comp = IndepVarComp()
            comp.add_output('incidence_angle',
                            val=incidence_angle,
                            shape=shape)
            comp.add_design_var('incidence_angle',
                                lower=-8. * np.pi / 180.,
                                upper=10. * np.pi / 180.)
            group.add_subsystem('inputs_comp', comp, promotes=['*'])

            comp = LinearCombinationComp(
                shape=shape,
                out_name='angle_of_attack',
                coeffs_dict=dict(
                    alpha=1.,
                    incidence_angle=1.,
                ),
            )
            group.add_subsystem('angle_of_attack_comp', comp, promotes=['*'])

            # Geometry -------------------------------------------------------

            comp = LinearCombinationComp(
                shape=shape,
                out_name='area',
                coeffs_dict=dict(
                    zip(['{}part_area'.format(side) for side in sides],
                        [1. for side in sides])))
            group.add_subsystem('area_comp', comp, promotes=['*'])

            if reference:
                comp = LinearCombinationComp(
                    shape=shape,
                    out_name='ref_area',
                    coeffs_dict=dict(area=1., ),
                )
                group.add_subsystem('ref_area_comp', comp, promotes=['*'])

            comp = LinearCombinationComp(
                shape=shape,
                out_name='span',
                coeffs_dict=dict(
                    zip(['{}part_span'.format(side) for side in sides],
                        [1. for side in sides])))
            group.add_subsystem('span_comp', comp, promotes=['*'])

            comp = PowerCombinationComp(shape=shape,
                                        out_name='span_2',
                                        powers_dict=dict(span=2))
            group.add_subsystem('span_2_comp', comp, promotes=['*'])

            comp = PowerCombinationComp(shape=shape,
                                        out_name='aspect_ratio',
                                        powers_dict=dict(span_2=1, area=-1))
            group.add_subsystem('aspect_ratio_comp', comp, promotes=['*'])

            # Flow properties -------------------------------------------------------

            comp = PowerCombinationComp(shape=shape,
                                        out_name='mach_number',
                                        powers_dict=dict(speed=1,
                                                         sonic_speed=-1))
            group.add_subsystem('mach_number_comp', comp, promotes=['*'])

            comp = ReynoldsComp(
                shape=shape,
                v_name='speed',
                L_name='mac',
                Re_name='reynolds_number',
            )
            group.add_subsystem('reynolds_number_comp', comp, promotes=['*'])

            # Lift -------------------------------------------------------

            comp = LiftCurveSlopeTmpComp(shape=shape)
            group.add_subsystem('lift_curve_slope_tmp_comp',
                                comp,
                                promotes=['*'])

            comp = LiftCurveSlopeComp(shape=shape, F=lifting_surface.F)
            group.add_subsystem('lift_curve_slope_comp', comp, promotes=['*'])

            comp = LiftCoeffComp(shape=shape, CL0=lifting_surface.CL0)
            comp.add_constraint('lift_coeff', upper=lifting_surface.CLmax)
            group.add_subsystem('lift_coeff_comp', comp, promotes=['*'])

            comp = ForceComp(shape=shape,
                             coeff_name='lift_coeff',
                             force_name='lift')
            group.add_subsystem('lift_comp', comp, promotes=['*'])

            # Parasitic drag -------------------------------------------------------

            comp = SkinFrictionCoeffComp(shape=shape)
            group.add_subsystem('skin_friction_coeff_comp',
                                comp,
                                promotes=['*'])

            comp = LiftingSurfaceFFComp(
                shape=shape,
                x_c_max_camber=lifting_surface.x_c_max_camber,
                t_c=lifting_surface.t_c,
            )
            group.add_subsystem('lifting_surface_ff_comp',
                                comp,
                                promotes=['*'])

            comp = ParasiticDragCoeffComp(shape=shape, Q=lifting_surface.Q)
            group.add_subsystem('parasitic_drag_coeff_comp',
                                comp,
                                promotes=['*'])

            # Induced drag ----------------------------------------------------

            comp = OswaldEfficiencyComp(shape=shape)
            group.add_subsystem('oswald_efficiency_comp', comp, promotes=['*'])

            comp = InducedDragCoeffComp(shape=shape)
            group.add_subsystem('induced_drag_coeff_comp',
                                comp,
                                promotes=['*'])

            # Total drag ------------------------------------------------------

            comp = LinearCombinationComp(
                shape=shape,
                out_name='drag_coeff',
                coeffs_dict=dict(parasitic_drag_coeff=1.,
                                 induced_drag_coeff=1.),
            )
            group.add_subsystem('drag_coeff_comp', comp, promotes=['*'])

            comp = ForceComp(shape=shape,
                             coeff_name='drag_coeff',
                             force_name='drag')
            group.add_subsystem('drag_comp', comp, promotes=['*'])

            # -------------------------------------------------------

            if reference:
                promotes = ['ref_area']
            else:
                promotes = None
            self.add_subsystem('{}_aerodynamics_group'.format(name),
                               group,
                               promotes=promotes)

        for miscellaneous_part in aircraft.miscellaneous_parts:
            name = miscellaneous_part['name']
            mirror = miscellaneous_part['mirror']
            CDp = miscellaneous_part['CDp']
            area = miscellaneous_part['ref_area']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group = Group()

                comp = IndepVarComp()
                comp.add_output('parasitic_drag_coeff', val=CDp, shape=shape)
                comp.add_output('induced_drag_coeff', val=0., shape=shape)
                comp.add_output('area', val=area, shape=shape)
                group.add_subsystem('parasitic_drag_comp',
                                    comp,
                                    promotes=['*'])

                comp = LinearCombinationComp(
                    shape=shape,
                    out_name='drag_coeff',
                    coeffs_dict=dict(parasitic_drag_coeff=1.,
                                     induced_drag_coeff=1.),
                )
                group.add_subsystem('drag_coeff_comp', comp, promotes=['*'])

                comp = ForceComp(shape=shape,
                                 coeff_name='drag_coeff',
                                 force_name='drag')
                group.add_subsystem('drag_comp', comp, promotes=['*'])

                self.add_subsystem('{}_aerodynamics_group'.format(side + name),
                                   group,
                                   promotes=promotes)

        lift_names = []
        drag_names = []
        for lifting_surface in aircraft.lifting_surfaces:
            name = lifting_surface.name

            lift_names.append('{}_aerodynamics_group_lift'.format(name))
            drag_names.append('{}_aerodynamics_group_drag'.format(name))

        for miscellaneous_part in aircraft.miscellaneous_parts:
            name = miscellaneous_part['name']
            mirror = miscellaneous_part['mirror']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                drag_names.append('{}_aerodynamics_group_drag'.format(side +
                                                                      name))

        comp = LinearCombinationComp(
            shape=shape,
            out_name='total_lift',
            coeffs_dict=dict(zip(lift_names, [1.] * len(lift_names))),
        )
        self.add_subsystem('total_lift_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='total_drag',
            coeffs_dict=dict(zip(drag_names, [1.] * len(drag_names))),
        )
        self.add_subsystem('total_drag_comp', comp, promotes=['*'])

        comp = ForceCoeffComp(
            shape=shape,
            coeff_name='total_lift_coeff',
            force_name='total_lift',
            area_name='ref_area',
        )
        self.add_subsystem('total_lift_coeff_comp', comp, promotes=['*'])

        comp = ForceCoeffComp(
            dict(
                shape=shape,
                coeff_name='total_drag_coeff',
                force_name='total_drag',
                area_name='ref_area',
            ))
        self.add_subsystem('total_drag_coeff_comp', comp, promotes=['*'])

    def connect_dependencies(self, group):
        aircraft = self.options['aircraft']

        for lifting_surface in aircraft.lifting_surfaces:
            name = lifting_surface.name
            mirror = lifting_surface.mirror

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group.connect(
                    '{}_geometry_group.part_area'.format(side + name),
                    '{}_aerodynamics_group.{}part_area'.format(name, side),
                )
                group.connect(
                    '{}_geometry_group.part_span'.format(side + name),
                    '{}_aerodynamics_group.{}part_span'.format(name, side),
                )
            group.connect(
                '{}_geometry_group.mac'.format(sides[0] + name),
                '{}_aerodynamics_group.mac'.format(name),
            )
            group.connect(
                '{}_geometry_group.sweep'.format(sides[0] + name),
                '{}_aerodynamics_group.sweep'.format(name),
            )
            group.connect(
                'alpha',
                '{}_aerodynamics_group.alpha'.format(name),
            )
            group.connect(
                'speed',
                '{}_aerodynamics_group.speed'.format(name),
            )
            group.connect(
                'sonic_speed',
                '{}_aerodynamics_group.sonic_speed'.format(name),
            )
            group.connect(
                'density',
                '{}_aerodynamics_group.density'.format(name),
            )
            group.connect(
                'dynamic_viscosity_1e_6',
                '{}_aerodynamics_group.dynamic_viscosity_1e_6'.format(name),
            )

        for miscellaneous_part in aircraft.miscellaneous_parts:
            name = miscellaneous_part['name']
            mirror = miscellaneous_part['mirror']
            weight = miscellaneous_part['weight']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group.connect(
                    'speed',
                    '{}_aerodynamics_group.speed'.format(side + name),
                )
                group.connect(
                    'density',
                    '{}_aerodynamics_group.density'.format(side + name),
                )
