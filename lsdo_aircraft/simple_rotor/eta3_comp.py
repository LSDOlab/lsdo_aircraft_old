import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


eps = 1e-6

class Eta3Comp(ArrayExplicitComponent):

    def array_initialize(self):
        self.options.declare('blade_solidity')

    def array_setup(self):
        self.array_add_input('eta2')
        self.array_add_input('power_coeff')
        self.array_add_input('blade_drag_coeff')
        self.array_add_input('glauert_factor')
        self.array_add_output('eta3')

        self.array_declare_partials('eta3', 'eta2')
        self.array_declare_partials('eta3', 'power_coeff')
        self.array_declare_partials('eta3', 'blade_drag_coeff')
        self.array_declare_partials('eta3', 'glauert_factor')

    def compute(self, inputs, outputs):
        blade_solidity = self.options['blade_solidity']

        eta2 = inputs['eta2']
        power_coeff = inputs['power_coeff']
        blade_drag_coeff = inputs['blade_drag_coeff']
        glauert_factor = inputs['glauert_factor']

        outputs['eta3'] = 1. - np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff * glauert_factor

    def compute_partials(self, inputs, partials):
        blade_solidity = self.options['blade_solidity']

        eta2 = inputs['eta2'].flatten()
        power_coeff = inputs['power_coeff'].flatten()
        blade_drag_coeff = inputs['blade_drag_coeff'].flatten()
        glauert_factor = inputs['glauert_factor'].flatten()

        partials['eta3', 'eta2'] = (
            -2 * np.pi ** 4 / 8. * eta2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff * glauert_factor
        ).flatten()
        partials['eta3', 'power_coeff'] = (
            np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) ** 2 * blade_solidity * blade_drag_coeff * glauert_factor
        ).flatten()
        partials['eta3', 'blade_drag_coeff'] = (
            -np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * glauert_factor
        ).flatten()
        partials['eta3', 'glauert_factor'] = (
            -np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff
        ).flatten()


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('eta2', np.random.random(shape))
    comp.add_output('power_coeff', np.random.random(shape))
    comp.add_output('blade_drag_coeff', np.random.random(shape))
    comp.add_output('glauert_factor', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = Eta3Comp(shape=shape, blade_solidity=0.4)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)