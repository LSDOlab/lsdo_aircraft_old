import numpy as np

from openmdao.api import Group, IndepVarComp

from lsdo_utils.comps.arithmetic_comps.linear_combination_comp import LinearCombinationComp
from lsdo_utils.comps.arithmetic_comps.ks_comp import KSComp
from lsdo_utils.comps.arithmetic_comps.scaling_comp import ScalingComp
from lsdo_utils.comps.array_comps.array_reshape_comp import ArrayReshapeComp
from lsdo_utils.comps.array_comps.scalar_expansion_comp import ScalarExpansionComp

from lsdo_aircraft.aerodynamics.dynamic_pressure_comp import DynamicPressureComp

from lsdo_aircraft.weights.wing_weight_comp import WingWeightComp
from lsdo_aircraft.weights.htail_weight_comp import HTailWeightComp
from lsdo_aircraft.weights.motor_weight_comp import MotorWeightComp
from lsdo_aircraft.weights.cg_comp import CGComp
from lsdo_aircraft.weights.max_2_comp import Max2Comp
from lsdo_aircraft.api import Aircraft, Rotor, LiftingSurface, MiscellaneousPart


class WeightsGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Aircraft)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']

        size = int(np.prod(shape))

        comp = IndepVarComp()
        comp.add_output('gross_weight_guess', shape=shape)
        comp.add_design_var('gross_weight_guess', lower=0.)
        # comp.add_output('gross_weight_guess_scalar')
        # comp.add_design_var('gross_weight_guess_scalar', lower=0., scaler=1.e-3)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        # comp = ScalarExpansionComp(
        #     shape=shape,
        #     in_name='gross_weight_guess_scalar',
        #     out_name='gross_weight_guess',
        # )
        # self.add_subsystem('gross_weight_guess_comp', comp, promotes=['*'])

        comp = DynamicPressureComp(
            shape=shape,
            rho_name='density',
            v_name='speed',
            dynamic_pressure_name='dynamic_pressure',
        )
        self.add_subsystem('dynamic_pressure_comp', comp, promotes=['*'])

        comp = ArrayReshapeComp(
            in_name='dynamic_pressure',
            out_name='dynamic_pressure_tmp',
            in_shape=shape,
            out_shape=(1, size),
        )
        self.add_subsystem('dynamic_pressure_reshape_comp',
                           comp,
                           promotes=['*'])

        comp = KSComp(
            in_name='dynamic_pressure_tmp',
            out_name='max_dynamic_pressure_scalar',
            shape=(1, ),
            constraint_size=size,
            lower_flag=False,
            rho=100.,
            bound=0.,
        )
        self.add_subsystem('max_dynamic_pressure_scalar_comp',
                           comp,
                           promotes=['*'])

        comp = ScalarExpansionComp(
            shape=shape,
            in_name='max_dynamic_pressure_scalar',
            out_name='max_dynamic_pressure',
        )
        self.add_subsystem('max_dynamic_pressure_comp', comp, promotes=['*'])

        part_group_names = []

        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            mirror = lifting_surface['mirror']
            reference = lifting_surface['reference']
            type_ = lifting_surface['type_']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            group = Group()

            if type_ == 'wing':
                comp = WingWeightComp(shape=shape,
                                      lifting_surface=lifting_surface)
            elif type_ == 'htail':
                comp = HTailWeightComp(shape=shape,
                                       lifting_surface=lifting_surface)
            group.add_subsystem('lifting_surface_weight_comp',
                                comp,
                                promotes=['*'])

            self.add_subsystem('{}_weights_group'.format(name), group)
            part_group_names.append(name)

        for rotor in aircraft['rotors']:
            name = rotor['name']
            mirror = rotor['mirror']
            rotor_weight_frac = rotor['rotor_weight_frac']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group = Group()

                comp = ArrayReshapeComp(
                    in_name='power',
                    out_name='power_tmp',
                    in_shape=shape,
                    out_shape=(1, size),
                )
                group.add_subsystem('power_reshape_comp', comp, promotes=['*'])

                comp = KSComp(
                    in_name='power_tmp',
                    out_name='max_power_scalar_tmp',
                    shape=(1, ),
                    constraint_size=size,
                    lower_flag=False,
                    rho=100.,
                    bound=0.,
                )
                group.add_subsystem('max_power_scalar_tmp_comp',
                                    comp,
                                    promotes=['*'])

                self.add_subsystem('{}_weights_tmp_group'.format(side + name),
                                   group)

            if len(sides) == 1:
                raise Exception()

            comp = Max2Comp(
                in1_name='left_max_power_scalar_tmp',
                in2_name='right_max_power_scalar_tmp',
                out_name='max_power_scalar',
                rho=100.,
            )
            self.add_subsystem('{}_weights_tmp_comp'.format(name), comp)

            for side in sides:
                group = Group()

                comp = ScalarExpansionComp(
                    shape=shape,
                    in_name='max_power_scalar',
                    out_name='max_power',
                )
                group.add_subsystem('max_power_comp', comp, promotes=['*'])

                comp = MotorWeightComp(shape=shape, rotor=rotor)
                group.add_subsystem('motor_weight_comp', comp, promotes=['*'])

                comp = ScalingComp(
                    shape=shape,
                    in_name='motor_weight',
                    out_name='rotor_weight',
                    c=rotor_weight_frac,
                )
                group.add_subsystem('rotor_weight_comp', comp, promotes=['*'])

                comp = LinearCombinationComp(
                    shape=shape,
                    in_names=['motor_weight', 'rotor_weight'],
                    out_name='weight',
                    coeffs=[1., 1.],
                )
                group.add_subsystem('weight_comp', comp, promotes=['*'])

                self.add_subsystem('{}_weights_group'.format(side + name),
                                   group)
                part_group_names.append('{}'.format(side + name))

        for miscellaneous_part in aircraft['miscellaneous_parts']:
            name = miscellaneous_part['name']
            mirror = miscellaneous_part['mirror']
            weight = miscellaneous_part['weight']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group = Group()

                comp = IndepVarComp()
                comp.add_output('weight_scalar', val=weight)
                group.add_subsystem('inputs_comp', comp, promotes=['*'])

                comp = ScalarExpansionComp(
                    shape=shape,
                    in_name='weight_scalar',
                    out_name='weight',
                )
                group.add_subsystem('weight_comp', comp, promotes=['*'])

                self.add_subsystem('{}_weights_group'.format(side + name),
                                   group)
                part_group_names.append('{}'.format(side + name))

        comp = LinearCombinationComp(
            shape=shape,
            in_names=[
                '{}_weight'.format(part_group_name)
                for part_group_name in part_group_names
            ],
            out_name='gross_weight',
            coeffs=[1. for part_group_name in part_group_names],
        )
        self.add_subsystem('gross_weight_comp', comp, promotes=['*'])

        comp = CGComp(
            shape=shape,
            weight_names=[
                '{}_weight'.format(part_group_name)
                for part_group_name in part_group_names
            ],
            cg_names=[
                '{}_cg'.format(part_group_name)
                for part_group_name in part_group_names
            ],
        )
        self.add_subsystem('cg_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            in_names=[
                'gross_weight',
                'gross_weight_guess',
            ],
            out_name='gross_weight_constraint',
            coeffs=[1., -1.],
        )
        self.add_subsystem('gross_weight_constraint_comp',
                           comp,
                           promotes=['*'])

        comp = ScalingComp(
            shape=shape,
            in_name='gross_weight_constraint',
            out_name='gross_weight_constraint_kN',
            c=1.e-3,
        )
        comp.add_constraint('gross_weight_constraint_kN', equals=0.)
        self.add_subsystem('gross_weight_constraint_kN_comp',
                           comp,
                           promotes=['*'])

    def connect_dependencies(self, group):
        aircraft = self.options['aircraft']

        part_group_names = []

        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            mirror = lifting_surface['mirror']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            group.connect(
                '{}_aerodynamics_group.area'.format(name),
                '{}_weights_group.area'.format(name),
            )
            group.connect(
                'max_dynamic_pressure',
                '{}_weights_group.max_dynamic_pressure'.format(name),
            )
            group.connect(
                '{}_aerodynamics_group.aspect_ratio'.format(name),
                '{}_weights_group.aspect_ratio'.format(name),
            )
            group.connect(
                '{}_geometry_group.sweep_deg'.format(sides[0] + name),
                '{}_weights_group.sweep_deg'.format(name),
            )
            group.connect(
                '{}_geometry_group.taper_ratio'.format(sides[0] + name),
                '{}_weights_group.taper_ratio'.format(name),
            )
            group.connect(
                'gross_weight_guess',
                '{}_weights_group.gross_weight'.format(name),
            )
            group.connect(
                '{}_weights_group.weight'.format(name),
                '{}_weight'.format(name),
            )
            group.connect(
                '{}_geometry_group.cg'.format(sides[0] + name),
                '{}_cg'.format(name),
            )

        for rotor in aircraft['rotors']:
            name = rotor['name']
            mirror = rotor['mirror']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                part_group_names.append('{}'.format(side + name))

                group.connect(
                    '{}_propulsor_group.power'.format(side + name),
                    '{}_weights_tmp_group.power'.format(side + name),
                )
                # group.connect(
                #     'gross_weight_guess',
                #     '{}_weights_group.gross_weight'.format(side + name),
                # )
                group.connect(
                    '{}_weights_group.weight'.format(side + name),
                    '{}_weight'.format(side + name),
                )
                group.connect(
                    '{}_geometry_group.cg'.format(side + name),
                    '{}_cg'.format(side + name),
                )
                group.connect(
                    '{}_weights_tmp_group.max_power_scalar_tmp'.format(side +
                                                                       name),
                    '{}_weights_tmp_comp.{}max_power_scalar_tmp'.format(
                        name, side),
                )
                group.connect(
                    '{}_weights_tmp_comp.max_power_scalar'.format(name),
                    '{}_weights_group.max_power_scalar'.format(side + name),
                )

        for miscellaneous_part in aircraft['miscellaneous_parts']:
            name = miscellaneous_parts['name']
            mirror = miscellaneous_parts['mirror']
            weight = miscellaneous_parts['weight']

            if mirror:
                sides = ['left_', 'right_']
            else:
                sides = ['']

            for side in sides:
                group.connect(
                    '{}_weights_group.weight'.format(side + name),
                    '{}_weight'.format(side + name),
                )
                group.connect(
                    '{}_geometry_group.cg'.format(side + name),
                    '{}_cg'.format(side + name),
                )
