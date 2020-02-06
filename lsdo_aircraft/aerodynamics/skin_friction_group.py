import numpy as np

from openmdao.api import Group

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, GeneralOperationComp, ElementwiseMinComp


class SkinFrictionGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=OptionsDictionary)
        self.options.declare('part', types=OptionsDictionary)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        part = self.options['part']

        skin_friction_roughness = part['skin_friction_roughness']
        laminar_pctg = part['laminar_pctg']
            
        comp = PowerCombinationComp(
            shape=shape,
            out_name='Re',
            powers_dict=dict(
                density=1.,
                speed=1.,
                characteristic_length=1.,
                dynamic_viscosity=-1.,
            ),
        )
        self.add_subsystem('Re_comp', comp, promotes=['*'])

        if aircraft['regime'] == 'subsonic':
            comp = PowerCombinationComp(
                shape=shape,
                out_name='Re_cutoff',
                coeff=38.21 * skin_friction_roughness ** -1.053,
                powers_dict=dict(
                    characteristic_length=1.053,
                ),
            )
            self.add_subsystem('Re_cutoff_comp', comp, promotes=['*'])
        elif aircraft['regime'] in ['transonic', 'supersonic']:
            comp = PowerCombinationComp(
                shape=shape,
                out_name='Re_cutoff',
                coeff=44.62 * skin_friction_roughness ** -1.053,
                powers_dict=dict(
                    characteristic_length=1.053,
                    mach_number=1.16,
                ),
            )
            self.add_subsystem('Re_cutoff_comp', comp, promotes=['*'])
        else:
            raise Exception()

        comp = ElementwiseMinComp(
            shape=shape, 
            out_name='Re_turbulent_min', 
            in_names=['Re', 'Re_cutoff'], 
            rho=1e-3,
        )
        self.add_subsystem('Re_turbulent_min_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='skin_friction_coeff_laminar',
            coeff=1.328,
            powers_dict=dict(
                Re=-0.5,
            ),
        )
        self.add_subsystem('skin_friction_coeff_laminar_comp', comp, promotes=['*'])

        def func(Re, M):
            Cf = 0.455 / ( np.log(Re) / np.log(10) ) ** 2.58 / (1 + 0.144 * M ** 2) ** 0.65
            return Cf

        def deriv(Re, M):
            dCf_dRe = -2.58 * 0.455 / ( np.log(Re) / np.log(10) ) ** 3.58 * 1 / Re / np.log(10) / (1 + 0.144 * M ** 2) ** 0.65
            dCf_dM = 0.455 / ( np.log(Re) / np.log(10) ) ** 2.58 * -0.65 / (1 + 0.144 * M ** 2) ** 1.65 * 2 * 0.144 * M
            return (dCf_dRe, dCf_dM)

        comp = GeneralOperationComp(
            shape=shape,
            out_name='skin_friction_coeff_turbulent',
            in_names=['Re_turbulent_min', 'mach_number'],
            func=func,
            deriv=deriv,
        )
        self.add_subsystem('skin_friction_coeff_turbulent_comp', comp, promotes=['*'])

        comp = LinearCombinationComp(
            shape=shape,
            out_name='skin_friction_coeff',
            coeffs_dict=dict(
                skin_friction_coeff_laminar=laminar_pctg / 100.,
                skin_friction_coeff_turbulent=1 - laminar_pctg / 100.,
            ),
        )
        self.add_subsystem('skin_friction_coeff_comp', comp, promotes=['*'])