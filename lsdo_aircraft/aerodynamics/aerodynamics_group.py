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
from lsdo_aircraft.aerodynamics.wave_drag_coeff_comp import \
    WaveDragCoeffComp
from lsdo_aircraft.aerodynamics.critical_mach_comp import \
    CriticalMachComp
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


class AerodynamicsGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Body)
        # self.options.declare('fltcond', types=FlightCondition)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        # fltcond = self.options['fltcond']

        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            sweep_deg = lifting_surface['sweep_deg']
            mac = lifting_surface['mac']

            group = Group()

            comp = IndepVarComp()
            # comp.add_output('incidence_angle', val=0., shape=shape)
            comp.add_output('sweep_deg', val=sweep_deg, shape=shape)
            comp.add_output('mac', val=mac, shape=shape)
            # comp.add_design_var('incidence_angle',
            #                     lower=-8. * np.pi / 180.,
            #                     upper=10. * np.pi / 180.)
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

            comp = LinearCombinationComp(shape=shape,
                                         out_name='area',
                                         coeffs_dict=dict(part_area=1.))
            group.add_subsystem('area_comp', comp, promotes=['*'])

            # if reference:
            #     comp = LinearCombinationComp(
            #         shape=shape,
            #         out_name='ref_area',
            #         coeffs_dict=dict(area=1., ),
            #     )
            #     group.add_subsystem('ref_area_comp', comp, promotes=['*'])

            comp = LinearCombinationComp(shape=shape,
                                         out_name='span',
                                         coeffs_dict=dict(part_span=1.))
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

            comp = LiftCurveSlopeComp(shape=shape, F=lifting_surface['F'])
            group.add_subsystem('lift_curve_slope_comp', comp, promotes=['*'])

            comp = LiftCoeffComp(shape=shape, CL0=lifting_surface['CL0'])
            comp.add_constraint('lift_coeff', upper=lifting_surface['CLmax'])
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
                x_c_max_camber=lifting_surface['x_c_max_camber'],
                t_c=lifting_surface['t_c'],
            )
            group.add_subsystem('lifting_surface_ff_comp',
                                comp,
                                promotes=['*'])

            comp = ParasiticDragCoeffComp(shape=shape, Q=lifting_surface['Q'])
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

            # Wave drag ----------------------------------------------------

            comp = CriticalMachComp(shape=shape)
            group.add_subsystem('critical_mach_comp', comp, promotes=['*'])
            comp = WaveDragCoeffComp(shape=shape)
            group.add_subsystem('wave_drag_coeff_comp', comp, promotes=['*'])

            # Total drag ------------------------------------------------------

            comp = LinearCombinationComp(
                shape=shape,
                out_name='drag_coeff',
                coeffs_dict=dict(parasitic_drag_coeff=1.,
                                 induced_drag_coeff=1.,
                                 wave_drag_coeff=0),
            )
            group.add_subsystem('drag_coeff_comp', comp, promotes=['*'])

            comp = ForceComp(shape=shape,
                             coeff_name='drag_coeff',
                             force_name='drag')
            group.add_subsystem('drag_comp', comp, promotes=['*'])

            # -------------------------------------------------------

            # if reference:
            #     promotes = ['ref_area', 'speed']
            # else:
            #     promotes = None

            promotes = ['speed', 'density']
            self.add_subsystem('{}_aerodynamics_group'.format(name),
                               group,
                               promotes=promotes)

        for nonlifting_surface in aircraft['nonlifting_surfaces']:
            name = nonlifting_surface['name']
            CDp = nonlifting_surface['CDp']
            area = nonlifting_surface['area']

            group = Group()

            comp = IndepVarComp()
            comp.add_output('parasitic_drag_coeff', val=CDp, shape=shape)
            comp.add_output('induced_drag_coeff', val=0., shape=shape)
            comp.add_output('area', val=area, shape=shape)
            group.add_subsystem('parasitic_drag_comp', comp, promotes=['*'])

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

            self.add_subsystem('{}_aerodynamics_group'.format(name),
                               group,
                               promotes=promotes)

        lift_names = []
        drag_names = []
        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']

            lift_names.append('{}_aerodynamics_group_lift'.format(name))
            drag_names.append('{}_aerodynamics_group_drag'.format(name))

        for nonlifting_surface in aircraft['nonlifting_surfaces']:
            name = nonlifting_surface['name']

            drag_names.append('{}_aerodynamics_group_drag'.format(name))

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
            area_name='area',
        )
        self.add_subsystem('total_lift_coeff_comp', comp, promotes=['*'])

        comp = ForceCoeffComp(
            shape=shape,
            coeff_name='total_drag_coeff',
            force_name='total_drag',
            area_name='area',
        )
        self.add_subsystem('total_drag_coeff_comp', comp, promotes=['*'])
        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            self.connect(
                '{}_aerodynamics_group.drag'.format(name),
                '{}_aerodynamics_group_drag'.format(name),
            )
            self.connect(
                '{}_aerodynamics_group.lift'.format(name),
                '{}_aerodynamics_group_lift'.format(name),
            )
        for nonlifting_surface in aircraft['nonlifting_surfaces']:
            name = nonlifting_surface['name']
            self.connect(
                '{}_aerodynamics_group.drag'.format(name),
                '{}_aerodynamics_group_drag'.format(name),
            )
