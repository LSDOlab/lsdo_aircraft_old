import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class BladeDragCoeffComp(ArrayExplicitComponent):

    def array_initialize(self):
        self.options.declare('integrated_design_lift_coeff', types=float)

    def array_setup(self):
        self.array_add_input('power_coeff')
        self.array_add_input('advance_ratio')
        self.array_add_output('blade_drag_coeff')

        self.array_declare_partials('blade_drag_coeff', 'power_coeff')
        self.array_declare_partials('blade_drag_coeff', 'advance_ratio')

    def compute(self, inputs, outputs):
        integrated_design_lift_coeff = self.options['integrated_design_lift_coeff']

        power_coeff = inputs['power_coeff']
        advance_ratio = inputs['advance_ratio']

        x = integrated_design_lift_coeff * power_coeff / advance_ratio

        outputs['blade_drag_coeff'] = -0.136 * x ** 2 + 0.116 * x + 0.00627

    def compute_partials(self, inputs, partials):
        integrated_design_lift_coeff = self.options['integrated_design_lift_coeff']

        power_coeff = inputs['power_coeff'].flatten()
        advance_ratio = inputs['advance_ratio'].flatten()

        x = integrated_design_lift_coeff * power_coeff / advance_ratio

        partials['blade_drag_coeff', 'power_coeff'] = (
            2 * -0.136 * x + 0.116
        ) * integrated_design_lift_coeff / advance_ratio
        partials['blade_drag_coeff', 'advance_ratio'] = (
            2 * -0.136 * x + 0.116
        ) * -integrated_design_lift_coeff * power_coeff / advance_ratio ** 2


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('power_coeff', np.random.random(shape))
    comp.add_output('advance_ratio', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = BladeDragCoeffComp(shape=shape, integrated_design_lift_coeff=0.2)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)