from openmdao.api import Group

from lsdo_aircraft.geometry.geometry import Geometry


class GeometryGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary', types=Geometry)

    def setup(self):
        shape = self.options['shape']
        options_dictionary = self.options['options_dictionary']

        for part in options_dictionary.children:
            name = part['name']
            group_class = part['group_class']

            group = group_class(shape=shape, options_dictionary=part)
            self.add_subsystem('{}_geometry_group'.format(name), group, promotes=group.promotes)