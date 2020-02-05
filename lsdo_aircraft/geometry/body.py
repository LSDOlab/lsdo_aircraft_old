from lsdo_utils.api import OptionsDictionary, float_types, units
from lsdo_aircraft.geometry.lifting_surface import LiftingSurface
from lsdo_aircraft.geometry.nonlifting_surface import NonliftingSurface
from lsdo_aircraft.simple_rotor.simple_rotor import SimpleRotor


class Body(OptionsDictionary):
    def initialize(self):
        self.declare('lifting_surfaces', default=[], types=list)
        self.declare('rotors', default=[], types=list)
        self.declare('nonlifting_surfaces', default=[], types=list)
        self.declare('parts', default=[], types=list)

    def add_part(self, part):
        if isinstance(part, LiftingSurface):
            self['lifting_surfaces'].append(part)

        if isinstance(part, SimpleRotor):
            self['rotors'].append(part)

        if isinstance(part, NonliftingSurface):
            # part['CDp'] *= self['CDp_margin']
            self['nonlifting_surfaces'].append(part)

        self['parts'].append(part)
