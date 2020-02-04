from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class DynamicPressureComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('rho_name', types=str)
        self.options.declare('v_name', types=str)
        self.options.declare('dynamic_pressure_name', types=str)

    def array_setup(self):
        self.rho_name = self.options['rho_name']
        self.v_name = self.options['v_name']
        self.dynamic_pressure_name = self.options['dynamic_pressure_name']

        self.array_add_input(self.rho_name)
        self.array_add_input(self.v_name)
        self.array_add_output(self.dynamic_pressure_name)
        self.array_declare_partials(self.dynamic_pressure_name, self.rho_name)
        self.array_declare_partials(self.dynamic_pressure_name, self.v_name)

    def compute(self, inputs, outputs):
        rho = inputs[self.rho_name]
        v = inputs[self.v_name]

        outputs[self.dynamic_pressure_name] = 0.5 * v**2 * rho

    def compute_partials(self, inputs, partials):
        rho = inputs[self.rho_name].flatten()
        v = inputs[self.v_name].flatten()

        partials[self.dynamic_pressure_name, self.rho_name] = 0.5 * v**2
        partials[self.dynamic_pressure_name, self.v_name] = v * rho
