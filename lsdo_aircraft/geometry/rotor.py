import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units

# from lsdo_aircraft.aerodynamics.aerodynamics_group import AerodynamicsGroup


class Rotor(OptionsDictionary):
    def initialize(self):
        self.declare('name', types=str)
        self.declare('lifting_surface_name', types=str)
        self.declare('u')
        self.declare('v')
        self.declare('offset', default={'x': 0, 'y': 0, 'z': 0}, types=dict)
        self.declare('sigma', default=0.4, types=float_types)
        self.declare('CLi', default=0.2, types=float_types)
        self.declare('mirror', default=True, types=bool)
        self.declare('rotor_weight_frac',
                     default=451. / 945.,
                     types=float_types)
        self.declare('tip_mach_constraint', default=0.55, types=float_types)
        self.declare('max_torque', default=500., types=float_types)
        self.declare('max_rotational_speed', default=1500., types=float_types)
        self.declare('max_RPM', default=None, types=float_types)
        self.declare('efficiency_power_system',
                     default=0.85,
                     types=float_types)
        self.declare('max_blade_loading_coeff',
                     default=0.14,
                     types=float_types)
        self.declare('motor_weight_multiplicative_factor',
                     default=1.75,
                     types=float_types)
        self.declare('motor_weight_additive_factor',
                     default=0.,
                     types=float_types)
        self.declare('stacked_factor', default=1., types=float_types)
        self.declare('lift_capable', default=True, types=bool)
        self.declare('cruise_capable', default=True, types=bool)

        if self['max_RPM'] is not None:
            self['max_rotational_speed'] = self['max_RPM'] / 60.
        self['lift_capable'] = float(self['lift_capable'])
        self['cruise_capable'] = float(self['cruise_capable'])
