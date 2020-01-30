from lsdo_utils.api import PowerCombinationComp, units, constants


class PropellerTakeoffWingLoadingComp(PowerCombinationComp):

    def pre_setup(self):
        self.options.update(dict(
            powers_dict=dict(
                TOP=1.,
                takeoff_density=1.,
                sealevel_density=-1.,
                CL_takeoff=1.,
                power_to_weight=1.,
            ),
            out_name='takeoff_wing_loading',
            coeff=units('N/m^2', 'lbf/ft^2') / 745.7 * units('N', 'lbf'),
        ))


class JetTakeoffWingLoadingComp(PowerCombinationComp):

    def pre_setup(self):
        self.options.update(dict(
            powers_dict=dict(
                TOP=1.,
                takeoff_density=1.,
                sealevel_density=-1.,
                CL_takeoff=1.,
                thrust_to_weight=1.,
            ),
            out_name='takeoff_wing_loading',
            coeff=units('N/m^2', 'lbf/ft^2'),
        ))