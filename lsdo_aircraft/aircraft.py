import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants


float_array_types = (int, float, np.ndarray)

class Aircraft(OptionsDictionary):
    """
       This options dictionary defines the openmdao options that will be used for aircraft design. The options are values that help define the aircraft, 
       but cannot be used as design variables for optimization. 
    """

    def initialize(self):
        self.declare('geometry', default=None, allow_none=True)
        self.declare('analyses', default=None, allow_none=True)
        self.declare('aircraft_type', values=[
            'ga_single',
            'ga_twin',
            'transport',
        ])
        self.declare('empty_weight_fraction_variable_sweep', default=False, types=bool)
        self.declare('empty_weight_fraction_weight_max', default=1.e8, types=float_array_types)
        self.declare('battery_energy_density_Wh_kg', default=150., types=float_array_types)
        self.declare('battery_energy_density', default=150., types=float_array_types)
        self.declare('propulsive_efficiency', default=0.85, types=float_array_types)
        self.declare('tsfc', default=1.e-4, types=float_array_types)
        self.declare('energy_source_type', default='electric', values=[
            'electric',
            'fuel_burning',
        ])
        self.declare('thrust_source_type', default='jet', values=[
            'propeller',
            'jet',
        ])
        self.declare('CL_max', default=1.5, types=float_array_types)
        self.declare('CL_takeoff', default=1.5, types=float_array_types)
        self.declare('climb_gradient', default=0.05, types=float_array_types)
        self.declare('turn_load_factor', default=2.5, types=float_array_types)
        self.declare('TOP', default=400., types=float_array_types)
        self.declare('takeoff_density', default=1.225, types=float_array_types)
        self.declare('stall_speed', default=1.225, types=float_array_types)
        self.declare('climb_speed', default=1.225, types=float_array_types)
        self.declare('turn_speed', default=1.225, types=float_array_types)

        self.declare('landing_distance', default=None, types=float_array_types, allow_none=True)
        self.declare('approach_distance', default=None, types=float_array_types, allow_none=True)

        self.declare('wing_loading', default=None, types=float_array_types, allow_none=True)
        self.declare('thrust_to_weight', default=0.5, types=float_array_types)

        self.declare('ref_wing_loading', default=None, types=float, allow_none=True)
        self.declare('ref_thrust_to_weight', default=0.5, types=float)

        self.declare('landing_distance_ft', default=6000., types=float_array_types)
        self.declare('wing_loading_lbf_ft2', default=100., types=float_array_types)
        self.declare('ref_wing_loading_lbf_ft2', default=100., types=float)

        self.declare('regime', default='transonic', values=['subsonic', 'transonic'])

        self.declare('powertrain', default=None, allow_none=True)

    def pre_setup(self):
        self.empty_weight_fraction_parameters = dict(
            ga_single=(2.36, -0.18),
            ga_twin=(1.51, -0.10),
            transport=(1.02, -0.06),
        )[self['aircraft_type']]

        if self['empty_weight_fraction_variable_sweep']:
            self.empty_weight_fraction_k_vs = 1.04
        else:
            self.empty_weight_fraction_k_vs = 1.

        self['battery_energy_density'] = self['battery_energy_density_Wh_kg'] * units('J/kg', 'Wh/kg')

        if self['aircraft_type'] in ['transport']:
            self['approach_distance'] = 1000. * units('m', 'ft')
        elif self['aircraft_type'] in ['ga_single', 'ga_twin']:
            self['approach_distance'] = 600. * units('m', 'ft')

        self['wing_loading'] = self['wing_loading_lbf_ft2'] * units('N/m^2', 'lbf/ft^2')
        self['ref_wing_loading'] = self['ref_wing_loading_lbf_ft2'] * units('N/m^2', 'lbf/ft^2')

        self['landing_distance'] = self['landing_distance_ft'] * units('m', 'ft')