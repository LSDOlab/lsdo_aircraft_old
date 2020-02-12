import numpy as np

from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import OptionsDictionary, LinearCombinationComp, PowerCombinationComp, GeneralOperationComp, LinearPowerCombinationComp, ElementwiseMinComp


class InducedDragGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('part', types=OptionsDictionary)

    def setup(self):
        shape = self.options['shape']
        part = self.options['part']

        comp = IndepVarComp()
        comp.add_output('sweep_30', val=30. * np.pi / 180., shape=shape)
        self.add_subsystem('sweep_30_comp', comp, promotes=['*'])

        comp = ElementwiseMinComp(
            shape=shape, 
            out_name='sweep_capped_30', 
            in_names=['sweep', 'sweep_30'], 
            rho=50.,
        )
        self.add_subsystem('sweep_capped_30_comp', comp, promotes=['*'])

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='oswald_efficiency_unswept',
            constant=1.14,
            terms_list=[
                (-1.78 * 0.045, dict(
                    aspect_ratio=0.68,
                )),
            ],
        )
        self.add_subsystem('oswald_efficiency_unswept_comp', comp, promotes=['*'])

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='oswald_efficiency_swept',
            constant=-3.1,
            terms_list=[
                (4.61, dict(
                    cos_sweep=0.15,
                )),
                (-4.61 * 0.045, dict(
                    aspect_ratio=0.68,
                    cos_sweep=0.15,
                )),
            ],
        )
        self.add_subsystem('oswald_efficiency_swept_comp', comp, promotes=['*'])

        comp = LinearPowerCombinationComp(
            shape=shape,
            out_name='oswald_efficiency',
            terms_list=[
                (1., dict(
                    oswald_efficiency_unswept=1.,
                )),
                (-1. / (30. * np.pi / 180.), dict(
                    oswald_efficiency_unswept=1.,
                    sweep_capped_30=1.,
                )),
                (1. / (30. * np.pi / 180.), dict(
                    oswald_efficiency_swept=1.,
                    sweep_capped_30=1.,
                )),
            ],
        )
        self.add_subsystem('oswald_efficiency_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='induced_drag_coeff',
            coeff=1. / np.pi,
            powers_dict=dict(
                lift_coeff=2.,
                oswald_efficiency=-1.,
                aspect_ratio=-1.,
            ),
        )
        self.add_subsystem('induced_drag_coeff_comp', comp, promotes=['*'])