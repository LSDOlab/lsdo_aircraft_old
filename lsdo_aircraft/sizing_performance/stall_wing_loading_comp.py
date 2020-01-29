from lsdo_utils.api import PowerCombinationComp


class StallWingLoadingComp(PowerCombinationComp):

    def pre_setup(self):
        self.options.update(dict(
            powers_dict=dict(
                CL_max=1.,
                density=1.,
                stall_speed=2.,
            ),
            out_name='stall_wing_loading',
            coeff=0.5,
        ))