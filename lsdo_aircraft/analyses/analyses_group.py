from openmdao.api import Group

from lsdo_utils.api import OptionsDictionary

from lsdo_aircraft.atmosphere.atmosphere_group import AtmosphereGroup

from lsdo_aircraft.geometry.lifting_surface_geometry import LiftingSurfaceGeometry
from lsdo_aircraft.geometry.body_geometry import BodyGeometry


class AnalysesGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=OptionsDictionary)
        self.options.declare('options_dictionary', types=OptionsDictionary)
        self.options.declare('geometry', types=OptionsDictionary)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        options_dictionary = self.options['options_dictionary']
        geometry = self.options['geometry']

        group = AtmosphereGroup(
            shape=shape,
            options_dictionary=object(),
        )
        self.add_subsystem('atmosphere_analysis_group', group, promotes=['*'])

        for analysis in options_dictionary.children:
            name = analysis['name']
            group_class = analysis['group_class']

            group = group_class(shape=shape, aircraft=aircraft, options_dictionary=analysis, geometry=geometry)
            self.add_subsystem('{}_analysis_group'.format(name), group, promotes=group.promotes)

    def connect_inputs(self, aircraft_group):
        options_dictionary = self.options['options_dictionary']
        geometry = self.options['geometry']

        for analysis in options_dictionary.children:
            analysis_name = analysis['name']
            group_class = analysis['group_class']

            for part in geometry.children:
                part_name = part['name']

                if isinstance(part, LiftingSurfaceGeometry):
                    dependent_variables = group_class.lifting_surface_dependent_variables
                elif isinstance(part, BodyGeometry):
                    dependent_variables = group_class.body_dependent_variables
                else:
                    dependent_variables = []

                for var_name in dependent_variables:
                    aircraft_group.connect(
                        '{}_geometry_group.{}'.format(part_name, var_name),
                        '{}_analysis_group.{}_group.{}'.format(analysis_name, part_name, var_name),
                    )