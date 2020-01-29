from __future__ import print_function
import numpy as np

from lsdo_utils.api import ArrayExplicitComponent

from lsdo_aircraft.atmosphere.constants import R


class DensityComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('pressure_MPa')
        self.array_add_input('temperature')
        self.array_add_output('density')
        self.array_declare_partials('density', 'pressure_MPa')
        self.array_declare_partials('density', 'temperature')

    def compute(self, inputs, outputs):
        p_Pa = inputs['pressure_MPa'] * 1e6
        temperature = inputs['temperature']

        outputs['density'] = p_Pa / R / temperature

    def compute_partials(self, inputs, partials):
        p_Pa = inputs['pressure_MPa'].flatten() * 1e6
        temperature = inputs['temperature'].flatten()

        partials['density', 'pressure_MPa'] = 1. / R / temperature * 1e6
        partials['density', 'temperature'] = -p_Pa / R / temperature ** 2