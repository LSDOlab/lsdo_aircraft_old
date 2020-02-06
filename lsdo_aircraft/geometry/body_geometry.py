import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants, float_types

from lsdo_aircraft.geometry.body_geometry_group import BodyGeometryGroup


float_array_types = (int, float, np.ndarray)

class BodyGeometry(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=BodyGeometryGroup, values=[BodyGeometryGroup])

        self.declare('fuselage_aspect_ratio', default=10., types=float_types)
        self.declare('interference_factor', default=1.0, types=float_types)

        self.declare('skin_friction_roughness', default=0.4e-5, types=float_types)
        self.declare('laminar_pctg', default=5., types=float_types)