import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class LiftCoeffComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('CL0', types=float)

    def array_setup(self):
        self.array_add_input('angle_of_attack')
        self.array_add_input('lift_curve_slope')
        self.array_add_output('lift_coeff')

        self.array_declare_partials('lift_coeff', 'angle_of_attack')
        self.array_declare_partials('lift_coeff', 'lift_curve_slope')

    def compute(self, inputs, outputs):
        CL0 = self.options['CL0']

        angle_of_attack = inputs['angle_of_attack']
        lift_curve_slope = inputs['lift_curve_slope']

        outputs['lift_coeff'] = CL0 + lift_curve_slope * angle_of_attack

    def compute_partials(self, inputs, partials):
        CL0 = self.options['CL0']

        angle_of_attack = inputs['angle_of_attack'].flatten()
        lift_curve_slope = inputs['lift_curve_slope'].flatten()

        partials['lift_coeff', 'angle_of_attack'] = lift_curve_slope
        partials['lift_coeff', 'lift_curve_slope'] = angle_of_attack


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('angle_of_attack', np.random.random(shape))
    comp.add_output('lift_curve_slope', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = LiftCoeffComp(shape=shape, CL0=0.2)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
