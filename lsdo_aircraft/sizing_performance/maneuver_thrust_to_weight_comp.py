import numpy as np

from lsdo_utils.api import LinearPowerCombinationComp


class ClimbThrustToWeightComp(LinearPowerCombinationComp):

    def pre_setup(self):
        self.options.update(dict(
            out_name='climb_thrust_to_weight',
            terms_list=[
                (1., dict(
                    climb_gradient=1.,
                )),
                (1. / 0.5 / np.pi, dict(
                    wing_loading=1.,
                    oswald_efficiency=-1.,
                    aspect_ratio=-1.,
                    density=-1.,
                    climb_speed=-2.,
                )),
                (0.5, dict(
                    CD0=1.,
                    density=1.,
                    climb_speed=2.,
                    wing_loading=-1.,
                )),
            ],
            constant=0.,
        ))


class TurnThrustToWeightComp(LinearPowerCombinationComp):

    def pre_setup(self):
        self.options.update(dict(
            out_name='turn_thrust_to_weight',
            terms_list=[
                (1. / 0.5 / np.pi, dict(
                    turn_load_factor=2.,
                    wing_loading=1.,
                    oswald_efficiency=-1.,
                    aspect_ratio=-1.,
                    density=-1.,
                    turn_speed=-2.,
                )),
                (0.5, dict(
                    CD0=1.,
                    density=1.,
                    turn_speed=2.,
                    wing_loading=-1.,
                )),
            ],
            constant=0.,
        ))