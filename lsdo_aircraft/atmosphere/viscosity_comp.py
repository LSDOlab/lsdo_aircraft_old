from __future__ import print_function
import numpy as np

from lsdo_utils.api import ArrayExplicitComponent

from lsdo_aircraft.atmosphere.constants import mu2, T2, Ts


class ViscosityComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('temperature')
        self.array_add_output('dynamic_viscosity_1e_6')
        self.array_declare_partials('dynamic_viscosity_1e_6', 'temperature')

    def compute(self, inputs, outputs):
        temperature = inputs['temperature']

        outputs['dynamic_viscosity_1e_6'] = mu2 * (temperature / T2) ** 1.5 * (T2 + Ts) / (temperature + Ts) / 1e-6

    def compute_partials(self, inputs, partials):
        temperature = inputs['temperature'].flatten()

        partials['dynamic_viscosity_1e_6', 'temperature'] = (
            1.5 * mu2 * temperature ** 0.5 / T2 ** 1.5 * (T2 + Ts) / (temperature + Ts) / 1e-6
            - mu2 * (temperature / T2) ** 1.5 * (T2 + Ts) / (temperature + Ts) ** 2 / 1e-6
        ).flatten()