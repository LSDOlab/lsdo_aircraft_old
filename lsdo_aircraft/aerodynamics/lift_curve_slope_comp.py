import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class LiftCurveSlopeComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('F', types=float)

    def array_setup(self):
        self.array_add_input('aspect_ratio')
        self.array_add_input('lift_curve_slope_tmp')
        self.array_add_output('lift_curve_slope')

        self.array_declare_partials('lift_curve_slope', 'aspect_ratio')
        self.array_declare_partials('lift_curve_slope', 'lift_curve_slope_tmp')

    def compute(self, inputs, outputs):
        F = self.options['F']

        aspect_ratio = inputs['aspect_ratio']
        lift_curve_slope_tmp = inputs['lift_curve_slope_tmp']

        outputs['lift_curve_slope'] = (2 * np.pi * aspect_ratio /
                                       (2. + lift_curve_slope_tmp**0.5) * F)

    def compute_partials(self, inputs, partials):
        F = self.options['F']

        aspect_ratio = inputs['aspect_ratio'].flatten()
        lift_curve_slope_tmp = inputs['lift_curve_slope_tmp'].flatten()

        partials['lift_curve_slope',
                 'aspect_ratio'] = (2 * np.pi /
                                    (2. + lift_curve_slope_tmp**0.5) * F)
        partials['lift_curve_slope', 'lift_curve_slope_tmp'] = (
            -np.pi * aspect_ratio / (2. + lift_curve_slope_tmp**0.5)**2 /
            lift_curve_slope_tmp**0.5 * F)


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('aspect_ratio', np.random.random(shape))
    comp.add_output('lift_curve_slope_tmp', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = LiftCurveSlopeComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
