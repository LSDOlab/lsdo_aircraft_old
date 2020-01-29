import numpy as np

from lsdo_utils.api import OptionsDictionary, float_types, units

from lsdo_aircraft.simple_battery.simple_battery_group import SimpleBatteryGroup


class SimpleBattery(OptionsDictionary):

    def initialize(self):
        self.declare('name', types=str)
        self.declare('group_class', default=SimpleBatteryGroup, values=[SimpleBatteryGroup])

        self.declare('specific_energy_Wh_kg', default=150., types=float_types)
        self.declare('specific_power_W_kg', default=200., types=float_types)
        self.declare('reserve_pct', default=20., types=float_types)

        self.declare('specific_energy', default=None, types=float_types, allow_none=True)
        self.declare('specific_power', default=None, types=float_types, allow_none=True)
        self.declare('reserve', default=None, types=float_types, allow_none=True)

    def pre_setup(self):
        self['specific_energy'] = self['specific_energy_Wh_kg'] * units('J/kg', 'Wh/kg')
        self['specific_power'] = self['specific_power_W_kg']
        self['reserve'] = self['reserve_pct'] / 100.