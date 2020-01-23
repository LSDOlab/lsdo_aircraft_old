from lsdo_utils.api import LinearPowerCombinationComp


class LandingWingLoadingComp(LinearPowerCombinationComp):

    def post_initialize(self):
        self.options.update(dict(
            out_name='landing_wing_loading',
            terms_list=[
                (1. / 80, dict(
                    landing_distance=1.,
                    takeoff_density=1.,
                    sealevel_density=-1.,
                    CL_max=1.,
                )),
                (-1. / 80, dict(
                    approach_distance=1.,
                    takeoff_density=1.,
                    sealevel_density=-1.,
                    CL_max=1.,
                )),
            ],
            constant=0.,
        ))