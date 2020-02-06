import numpy as np

from lsdo_utils.api import OptionsDictionary, units, constants, float_types

from lsdo_aircraft.geometry.part_geometry_group import PartGeometryGroup


float_array_types = (int, float, np.ndarray)

class PartGeometry(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=PartGeometryGroup, values=[PartGeometryGroup])

        self.declare('interference_factor', default=1.0, types=float_types)
        self.declare('parasite_drag_coeff', default=0.005, types=float_types)

        self.declare('skin_friction_roughness', default=0.4e-5, types=float_types)
        self.declare('laminar_pctg', default=5., types=float_types)