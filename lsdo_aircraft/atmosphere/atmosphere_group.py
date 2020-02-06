from __future__ import print_function
import numpy as np
from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import PowerCombinationComp

from lsdo_aircraft.atmosphere.temperature_comp import TemperatureComp
from lsdo_aircraft.atmosphere.pressure_comp import PressureComp
from lsdo_aircraft.atmosphere.density_comp import DensityComp
from lsdo_aircraft.atmosphere.sonic_speed_comp import SonicSpeedComp
from lsdo_aircraft.atmosphere.viscosity_comp import ViscosityComp


class AtmosphereGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('options_dictionary')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']

        size = int(np.prod(shape))

        group = Group()

        comp = PowerCombinationComp(
            shape=shape,
            out_name='altitude_km',
            coeff=1.e-3,
            powers_dict=dict(altitude=1., ),
        )
        self.add_subsystem('altitude_km_comp', comp, promotes=['*'])

        comp = TemperatureComp(shape=shape)
        self.add_subsystem('temperature_comp', comp, promotes=['*'])

        comp = PressureComp(shape=shape)
        self.add_subsystem('pressure_comp', comp, promotes=['*'])

        comp = DensityComp(shape=shape)
        self.add_subsystem('density_comp', comp, promotes=['*'])

        comp = SonicSpeedComp(shape=shape)
        self.add_subsystem('sonic_speed_comp', comp, promotes=['*'])

        comp = ViscosityComp(shape=shape)
        self.add_subsystem('viscosity_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='mach_number',
            powers_dict=dict(
                speed=1.,
                sonic_speed=-1.,
            ),
        )
        self.add_subsystem('mach_number_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='dynamic_pressure',
            coeff=0.5,
            powers_dict=dict(
                density=1.,
                speed=2.,
            ),
        )
        self.add_subsystem('dynamic_pressure_comp', comp, promotes=['*'])