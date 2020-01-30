import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class Eta2Comp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('eta1')
        self.array_add_input('power_coeff')
        self.array_add_input('advance_ratio')
        self.array_add_output('eta2')

        self.array_declare_partials('eta2', 'eta1')
        self.array_declare_partials('eta2', 'power_coeff')
        self.array_declare_partials('eta2', 'advance_ratio')

    def compute(self, inputs, outputs):
        eta1 = inputs['eta1']
        power_coeff = inputs['power_coeff']
        advance_ratio = inputs['advance_ratio']

        outputs['eta2'] = 1. - 4. / np.pi ** 3 * eta1 * power_coeff / advance_ratio

    def compute_partials(self, inputs, partials):
        eta1 = inputs['eta1'].flatten()
        power_coeff = inputs['power_coeff'].flatten()
        advance_ratio = inputs['advance_ratio'].flatten()

        partials['eta2', 'eta1'] = (
            -4. / np.pi ** 3 * power_coeff / advance_ratio
        ).flatten()
        partials['eta2', 'power_coeff'] = (
            -4. / np.pi ** 3 * eta1 / advance_ratio
        ).flatten()
        partials['eta2', 'advance_ratio'] = (
            4. / np.pi ** 3 * eta1 * power_coeff / advance_ratio ** 2
        ).flatten()


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('eta1', np.random.random(shape))
    comp.add_output('power_coeff', np.random.random(shape))
    comp.add_output('advance_ratio', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = Eta2Comp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)