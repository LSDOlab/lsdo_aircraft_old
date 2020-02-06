from openmdao.api import Group

from lsdo_aircraft.aircraft import Aircraft
from lsdo_aircraft.geometry.geometry_group import GeometryGroup
from lsdo_aircraft.analyses.analyses_group import AnalysesGroup


class AircraftGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Aircraft)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']

        geometry_group = GeometryGroup(
            shape=shape, 
            options_dictionary=aircraft['geometry'],
        )
        self.add_subsystem('geometry_group', geometry_group, promotes=['*'])

        analyses_group = AnalysesGroup(
            shape=shape, 
            aircraft=aircraft,
            geometry=aircraft['geometry'], 
            options_dictionary=aircraft['analyses'],
        )
        self.add_subsystem('analyses_group', analyses_group, promotes=['*'])
        analyses_group.connect_inputs(self)