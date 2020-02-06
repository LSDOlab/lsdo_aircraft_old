import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants, float_types

from lsdo_aircraft.geometry.lifting_surface_geometry_group import LiftingSurfaceGeometryGroup


float_array_types = (int, float, np.ndarray)

class LiftingSurfaceGeometry(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=LiftingSurfaceGeometryGroup, values=[LiftingSurfaceGeometryGroup])

        self.declare('lift_coeff_zero_alpha', default=0., types=float_types)
        self.declare('lift_curve_slope_2D', default=2 * np.pi, types=float_types)

        self.declare('dynamic_pressure_ratio', default=1., types=float_types)
        self.declare('downwash_slope', default=0., types=float_types)
        self.declare('wing_exposed_ratio', default=0.9, types=float_types)
        self.declare('fuselage_diameter_span', default=0.1, types=float_types)

        self.declare('skin_friction_roughness', default=0.4e-5, types=float_types)
        self.declare('laminar_pctg', default=5., types=float_types)

        self.declare('thickness_chord', default=0.1, types=float_types)
        self.declare('max_thickness_location', default=0.3, types=float_types)

        self.declare('interference_factor', default=1.0, types=float_types)

        self.declare('airfoil_technology_factor', default=0.95, types=float_types)