from lsdo_utils.api import OptionsDictionary, units, constants


class Aircraft(OptionsDictionary):
    """
       This options dictionary defines the openmdao options that will be used for aircraft design. The options are values that help define the aircraft, 
       but cannot be used as design variables for optimization. 
    """

    def initialize(self):
        self.declare('empty_weight_fraction_ac_type', values=[
            'ga_single',
            'ga_twin',
            'transport',
        ])
        self.declare('empty_weight_fraction_variable_sweep', default=False, types=bool)
        self.declare('empty_weight_fraction_weight_max', default=1.e8, types=float)
        self.declare('battery_energy_density_Wh_kg', default=150., types=float)
        self.declare('battery_energy_density', default=150., types=float)
        self.declare('propulsive_efficiency', default=0.85, types=float)
        self.declare('tsfc', default=1.e-4, types=float)
        self.declare('propulsion_type', default='electric', values=[
            'electric',
            'fuel_burning',
        ])


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

        self['battery_energy_density'] = self['battery_energy_density_Wh_kg'] * units('J/kg', 'Wh/kg')