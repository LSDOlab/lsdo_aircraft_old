import numpy as np

from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, LinearPowerCombinationComp, GeneralOperationComp, ElementwiseMinComp

from lsdo_aircraft.aerodynamics.lift_group import LiftGroup
from lsdo_aircraft.aerodynamics.induced_drag_group import InducedDragGroup
from lsdo_aircraft.aerodynamics.skin_friction_group import SkinFrictionGroup
from lsdo_aircraft.aerodynamics.wave_drag_coeff_comp import WaveDragCoeffComp
from lsdo_aircraft.geometry.lifting_surface_geometry import LiftingSurfaceGeometry
from lsdo_aircraft.geometry.body_geometry import BodyGeometry
from lsdo_aircraft.geometry.part_geometry import PartGeometry


class AerodynamicsGroup(Group):

    lifting_surface_dependent_variables = [
        'sweep',
        'aspect_ratio',
        'wetted_area',
        'area',
        'incidence_angle',
        'characteristic_length',
    ]

    body_dependent_variables = [
        'wetted_area',
        'characteristic_length',
    ]

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=OptionsDictionary)
        self.options.declare('geometry', types=OptionsDictionary)
        self.options.declare('options_dictionary', types=OptionsDictionary)

        self.promotes = [
            'density', 
            'speed', 
            'ref_area',
            'dynamic_viscosity', 
            'alpha', 
            'mach_number',
        ]

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        geometry = self.options['geometry']
        options_dictionary = self.options['options_dictionary']
        
        comp = IndepVarComp()
        comp.add_output('dummy_var')
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        for part in geometry.children:
            name = part['name']

            group = Group()

            # Passthrough for area

            if isinstance(part, LiftingSurfaceGeometry):
                comp = LinearCombinationComp(
                    shape=shape,
                    out_name='_area',
                    coeffs_dict=dict(
                        area=1.,
                    ),
                )
                group.add_subsystem('area_comp', comp, promotes=['*'])
            else:
                comp = IndepVarComp()
                comp.add_output('_area', shape=shape)
                group.add_subsystem('area_comp', comp, promotes=['*'])

            # Cosine of sweep - useful for many calculations that follow

            if isinstance(part, LiftingSurfaceGeometry):
                def func(sweep): 
                    return np.cos(sweep)

                def deriv(sweep):
                    return (-np.sin(sweep))

                comp = GeneralOperationComp(
                    shape=shape,
                    out_name='cos_sweep',
                    in_names=['sweep'],
                    func=func,
                    deriv=deriv,
                )
                group.add_subsystem('cos_sweep_comp', comp, promotes=['*'])

            # Lift coefficient

            if isinstance(part, LiftingSurfaceGeometry):
                lift_group = LiftGroup(
                    shape=shape,
                    part=part,
                )
                group.add_subsystem('lift_group', lift_group, promotes=['*'])
            elif isinstance(part, PartGeometry):
                comp = LinearCombinationComp(
                    shape=shape,
                    out_name='dummy_comp_var',
                    coeffs_dict=dict(
                        ref_area=1.,
                        alpha=1.,
                        wetted_area=1.,
                        characteristic_length=1.,
                    ),
                )
                group.add_subsystem('dummy_comp', comp, promotes=['*'])

                comp = IndepVarComp()
                comp.add_output('lift_coeff', val=0., shape=shape)
                group.add_subsystem('lift_coeff_comp', comp, promotes=['*'])
            else: 
                comp = LinearCombinationComp(
                    shape=shape,
                    out_name='dummy_comp_var',
                    coeffs_dict=dict(
                        alpha=1.,
                    ),
                )
                group.add_subsystem('dummy_comp', comp, promotes=['*'])

                comp = IndepVarComp()
                comp.add_output('lift_coeff', val=0., shape=shape)
                group.add_subsystem('lift_coeff_comp', comp, promotes=['*'])

            # Induced drag coefficient

            if isinstance(part, LiftingSurfaceGeometry):
                induced_drag_group = InducedDragGroup(
                    shape=shape,
                    part=part,
                )
                group.add_subsystem('induced_drag_group', induced_drag_group, promotes=['*'])
            else: 
                comp = IndepVarComp()
                comp.add_output('induced_drag_coeff', val=0., shape=shape)
                group.add_subsystem('induced_drag_coeff_comp', comp, promotes=['*'])

            # Skin friction coefficient
            
            skin_friction_group = SkinFrictionGroup(
                shape=shape,
                aircraft=aircraft,
                part=part,
            )
            group.add_subsystem('skin_friction_group', skin_friction_group, promotes=['*'])

            # Parasite drag coefficient---form factor

            if isinstance(part, LiftingSurfaceGeometry):          
                thickness_chord = part['thickness_chord']
                max_thickness_location = part['max_thickness_location']

                comp = PowerCombinationComp(
                    shape=shape,
                    out_name='form_factor',
                    coeff=1.34 * (1 + 0.6 / max_thickness_location * thickness_chord + 100. * thickness_chord ** 4),
                    powers_dict=dict(
                        mach_number=0.18,
                        cos_sweep=0.28,
                    ),
                )
                group.add_subsystem('form_factor_comp', comp, promotes=['*'])
            elif isinstance(part, BodyGeometry):  
                fuselage_aspect_ratio = part['fuselage_aspect_ratio']
                comp = IndepVarComp()
                comp.add_output('form_factor', val=1 + 60. / fuselage_aspect_ratio ** 3. + fuselage_aspect_ratio / 400., shape=shape)
                group.add_subsystem('form_factor_comp', comp, promotes=['*'])

            # Parasite drag coefficient---interference factor

            comp = IndepVarComp()
            comp.add_output('interference_factor', val=part['interference_factor'], shape=shape)
            group.add_subsystem('interference_factor_comp', comp, promotes=['*'])

            # Parasite drag coefficient

            if isinstance(part, (LiftingSurfaceGeometry, BodyGeometry)):    
                comp = PowerCombinationComp(
                    shape=shape,
                    out_name='parasite_drag_coeff',
                    powers_dict=dict(
                        skin_friction_coeff=1.,
                        form_factor=1.,
                        interference_factor=1.,
                        wetted_area=1.,
                        ref_area=-1.,
                    ),
                )
                group.add_subsystem('parasite_drag_coeff_comp', comp, promotes=['*'])
            elif isinstance(part, PartGeometry):   
                comp = IndepVarComp()
                comp.add_output('parasite_drag_coeff', val=part['parasite_drag_coeff'], shape=shape)
                group.add_subsystem('parasite_drag_coeff_comp', comp, promotes=['*'])
            else:
                comp = IndepVarComp()
                comp.add_output('parasite_drag_coeff', val=0., shape=shape)
                group.add_subsystem('parasite_drag_coeff_comp', comp, promotes=['*'])

            # Wave drag coefficient

            if isinstance(part, LiftingSurfaceGeometry):
                airfoil_technology_factor = part['airfoil_technology_factor']
                thickness_chord = part['thickness_chord']

                comp = LinearPowerCombinationComp(
                    shape=shape,
                    out_name='critical_mach_number',
                    constant=-(0.1 / 80.) ** (1. / 3.),
                    terms_list=[
                        (airfoil_technology_factor, dict(
                            cos_sweep=-1.,
                        )),
                        (-thickness_chord, dict(
                            cos_sweep=-2.,
                        )),
                        (-0.1, dict(
                            cos_sweep=-3.,
                            lift_coeff=1.,
                        )),
                    ],
                )
                group.add_subsystem('critical_mach_number_comp', comp, promotes=['*'])

                comp = WaveDragCoeffComp(shape=shape)
                group.add_subsystem('wave_drag_coeff_comp', comp, promotes=['*'])
            else:
                comp = IndepVarComp()
                comp.add_output('wave_drag_coeff', val=0., shape=shape)
                group.add_subsystem('wave_drag_coeff_comp', comp, promotes=['*'])

            self.add_subsystem('{}_group'.format(name), group, promotes=[
                'density', 
                'speed', 
                'ref_area',
                'dynamic_viscosity', 
                'alpha', 
                'mach_number',
            ])

        # 

        names = []
        lift_coeff_names = []
        lift_coeff_connects = []
        area_names = []
        area_connects = []
        for part in geometry.children:
            name = part['name']
            
            lift_coeff_name = '{}_group_lift_coeff'.format(name)
            src_lift_coeff_name = '{}_group.lift_coeff'.format(name)
            area_name = '{}_group_area'.format(name)
            src_area_name = '{}_group._area'.format(name)

            lift_coeff_names.append(lift_coeff_name)
            lift_coeff_connects.append((src_lift_coeff_name, lift_coeff_name))

            area_names.append(area_name)
            area_connects.append((src_area_name, area_name))

            names.append(name)

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='lift_coeff',
            terms_list=[
                (1., {
                    lift_coeff_name: 1.,
                    area_name: 1.,
                    'ref_area': -1.,
                })
                for lift_coeff_name, area_name in zip(lift_coeff_names, area_names)
            ],
        )
        self.add_subsystem('lift_coeff_comp', comp, promotes=['*'])

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='drag_coeff',
            terms_list=[
                (1., {
                    '{}_group_induced_drag_coeff'.format(name): 1.,
                    area_name: 1.,
                    'ref_area': -1.,
                })
                for name, area_name in zip(names, area_names)
            ] + [
                (1., {
                    '{}_group_parasite_drag_coeff'.format(name): 1.,
                    # area_name: 0.,
                    # 'ref_area': 0.,
                })
                for name, area_name in zip(names, area_names)
            ] + [
                (1., {
                    '{}_group_wave_drag_coeff'.format(name): 1.,
                    area_name: 1.,
                    'ref_area': -1.,
                })
                for name, area_name in zip(names, area_names)
            ],
        )
        self.add_subsystem('drag_coeff_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='lift_to_drag_ratio',
            powers_dict=dict(
                lift_coeff=1.,
                drag_coeff=-1.,
            ),
        )
        self.add_subsystem('lift_to_drag_ratio_comp', comp, promotes=['*'])
        
        for src, tgt in lift_coeff_connects:
            self.connect(src, tgt)

        for src, tgt in area_connects:
            self.connect(src, tgt)

        for name in names:
            self.connect(
                '{}_group.induced_drag_coeff'.format(name),
                '{}_group_induced_drag_coeff'.format(name),
            )
            self.connect(
                '{}_group.parasite_drag_coeff'.format(name),
                '{}_group_parasite_drag_coeff'.format(name),
            )
            self.connect(
                '{}_group.wave_drag_coeff'.format(name),
                '{}_group_wave_drag_coeff'.format(name),
            )