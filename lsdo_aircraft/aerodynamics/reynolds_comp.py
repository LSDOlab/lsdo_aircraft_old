from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class ReynoldsComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('v_name', types=str)
        self.options.declare('L_name', types=str)
        self.options.declare('Re_name', types=str)

    def array_setup(self):
        self.v_name = self.options['v_name']
        self.L_name = self.options['L_name']
        self.Re_name = self.options['Re_name']

        self.array_add_input('density')
        self.array_add_input('dynamic_viscosity_1e_6')
        self.array_add_input(self.v_name)
        self.array_add_input(self.L_name)
        self.array_add_output(self.Re_name)
        self.array_declare_partials(self.Re_name, 'density')
        self.array_declare_partials(self.Re_name, 'dynamic_viscosity_1e_6')
        self.array_declare_partials(self.Re_name, self.v_name)
        self.array_declare_partials(self.Re_name, self.L_name)

    def compute(self, inputs, outputs):
        density = inputs['density']
        mu_kg_ms = inputs['dynamic_viscosity_1e_6'] * 1e-6
        air_speed = inputs[self.v_name]
        L = inputs[self.L_name]

        outputs[self.Re_name] = density * air_speed * L / mu_kg_ms

    def compute_partials(self, inputs, partials):
        density = inputs['density'].flatten()
        mu_kg_ms = inputs['dynamic_viscosity_1e_6'].flatten() * 1e-6
        air_speed = inputs[self.v_name].flatten()
        L = inputs[self.L_name].flatten()

        partials[self.Re_name, 'density'] = air_speed * L / mu_kg_ms
        partials[
            self.Re_name,
            'dynamic_viscosity_1e_6'] = -density * air_speed * L / mu_kg_ms**2 * 1e-6
        partials[self.Re_name, self.v_name] = density * L / mu_kg_ms
        partials[self.Re_name, self.L_name] = density * air_speed / mu_kg_ms
