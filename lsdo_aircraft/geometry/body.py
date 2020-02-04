from lsdo_utils.api import OptionsDictionary, float_types, units
from lsdo_aircraft.geometry.lifting_surface import LiftingSurface
from lsdo_aircraft.geometry.rotor import Rotor
from lsdo_aircraft.geometry.miscellaneous_part import MiscellaneousPart

J_Wh = 1 / 0.000277778
N_kg = 9.81


class Body(OptionsDictionary):
    def initialize(self):
        self.declare('lifting_surfaces', types=list)
        self.declare('rotors', types=list)
        self.declare('miscellaneous_parts', types=list)
        self.declare('parts', types=list)
        self.declare('CDp_margin', default=1.2, types=float_types)
        self.declare('battery_energy_density',
                     default=200. * J_Wh / N_kg,
                     types=float_types)
        self.declare('battery_reserve', default=0.15, types=float_types)

    def add_part(self, part):
        if isinstance(part, LiftingSurface):
            self['lifting_surfaces'].append(part)

        if isinstance(part, Rotor):
            self['rotors'].append(part)

        if isinstance(part, MiscellaneousPart):
            part['CDp'] *= self['CDp_margin']
            self['miscellaneous_parts'].append(part)

        self['parts'].append(part)
