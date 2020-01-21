from lsdo_utils.api import OptionsDictionary, units, constants


class Aircraft(OptionsDictionary):

    def initialize(self):
        self.declare('empty_weight_fraction_ac_type', values=[
            'ga_single',
            'ga_twin',
            'transport',
        ])
        self.declare('empty_weight_fraction_variable_sweep', default=False, types=bool)
        self.declare('empty_weight_fraction_weight_max', default=1.e8, types=float)

    def post_initialize(self):
        self.empty_weight_fraction_parameters = dict(
            ga_single=(2.36, -0.18),
            ga_twin=(1.51, -0.10),
            transport=(1.02, -0.06),
        )[self['empty_weight_fraction_ac_type']]

        if self['empty_weight_fraction_variable_sweep']:
            self.empty_weight_fraction_k_vs = 1.04
        else:
            self.empty_weight_fraction_k_vs = 1.