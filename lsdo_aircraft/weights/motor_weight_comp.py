from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent

motor_mult = 1
esc_mult = 1


class MotorWeightComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('rotor')

    def array_setup(self):
        self.array_add_input('max_power')
        self.array_add_output('motor_weight')

        self.array_declare_partials('*', '*')

    def compute(self, inputs, outputs):
        multiplicative_factor = self.options[
            'rotor'].motor_weight_multiplicative_factor
        additive_factor = self.options['rotor'].motor_weight_additive_factor

        x = inputs['max_power'] / 1.e3

        outputs['motor_weight'] = (
            (-2e-5 * x**2 + 0.1595 * x + 3.3081) * 9.80665 * motor_mult +
            (0.062 * x + 0.3867) * 9.80665 *
            esc_mult) * multiplicative_factor + additive_factor

    def compute_partials(self, inputs, partials):
        multiplicative_factor = self.options[
            'rotor'].motor_weight_multiplicative_factor
        additive_factor = self.options['rotor'].motor_weight_additive_factor

        x = inputs['max_power'].flatten() / 1.e3

        partials['motor_weight', 'max_power'] = (
            (-4e-5 * x + 0.1595) / 1.e3 * 9.80665 * motor_mult +
            0.062 / 1.e3 * 9.80665 * esc_mult) * multiplicative_factor


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('max_power', val=np.random.random(shape))
    prob.model.add_subsystem('ivc', comp, promotes=['*'])

    comp = MotorWeightComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup()
    prob.run_model()
    prob.check_partials(compact_print=True)
