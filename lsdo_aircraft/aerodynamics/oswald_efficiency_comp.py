import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class OswaldEfficiencyComp(ArrayExplicitComponent):
    def array_setup(self):
        self.array_add_input('aspect_ratio')
        self.array_add_output('oswald_efficiency')

        self.array_declare_partials('oswald_efficiency', 'aspect_ratio')

    def compute(self, inputs, outputs):
        aspect_ratio = inputs['aspect_ratio']

        outputs['oswald_efficiency'] = 1.78 * (
            1. - 0.045 * aspect_ratio**0.68) - 0.64

    def compute_partials(self, inputs, partials):
        aspect_ratio = inputs['aspect_ratio'].flatten()

        partials['oswald_efficiency',
                 'aspect_ratio'] = 1.78 * -0.045 * 0.68 * aspect_ratio**-0.32


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('aspect_ratio', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = OswaldEfficiencyComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
