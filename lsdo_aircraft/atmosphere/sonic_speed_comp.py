from __future__ import print_function
import numpy as np

from lsdo_utils.api import ArrayExplicitComponent

from lsdo_aircraft.atmosphere.constants import gamma, R


class SonicSpeedComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('temperature')
        self.array_add_output('sonic_speed')
        self.array_declare_partials('sonic_speed', 'temperature')

    def compute(self, inputs, outputs):
        temperature = inputs['temperature']

        outputs['sonic_speed'] = np.sqrt(gamma * R * temperature)

    def compute_partials(self, inputs, partials):
        temperature = inputs['temperature'].flatten()

        partials['sonic_speed', 'temperature'] = 0.5 * np.sqrt(gamma * R / temperature)