from __future__ import print_function
import numpy as np

from lsdo_utils.api import ArrayExplicitComponent

from lsdo_aircraft.atmosphere.utils import \
    get_mask_arrays, compute_pressures, compute_pressure_derivs


class PressureComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('altitude_km')
        self.array_add_output('pressure_MPa')
        self.array_declare_partials('pressure_MPa', 'altitude_km')

    def compute(self, inputs, outputs):
        h_m = inputs['altitude_km'] * 1e3

        self.mask_arrays = get_mask_arrays(h_m)

        p_Pa = compute_pressures(h_m, *self.mask_arrays)

        outputs['pressure_MPa'] = p_Pa / 1e6

    def compute_partials(self, inputs, partials):
        h_m = inputs['altitude_km'] * 1e3
        derivs = compute_pressure_derivs(h_m, *self.mask_arrays).flatten()

        partials['pressure_MPa', 'altitude_km'] = derivs * 1e3 / 1e6