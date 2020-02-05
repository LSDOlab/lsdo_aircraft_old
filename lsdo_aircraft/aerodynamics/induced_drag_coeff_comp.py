import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class InducedDragCoeffComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('Q', types=float)

    def array_setup(self):
        self.array_add_input('lift_coeff')
        self.array_add_input('aspect_ratio')
        self.array_add_input('oswald_efficiency')
        self.array_add_output('induced_drag_coeff')

        self.array_declare_partials('induced_drag_coeff', 'lift_coeff')
        self.array_declare_partials('induced_drag_coeff', 'aspect_ratio')
        self.array_declare_partials('induced_drag_coeff', 'oswald_efficiency')

    def compute(self, inputs, outputs):
        lift_coeff = inputs['lift_coeff']
        aspect_ratio = inputs['aspect_ratio']
        oswald_efficiency = inputs['oswald_efficiency']

        outputs[
            'induced_drag_coeff'] = lift_coeff**2. / np.pi / oswald_efficiency / aspect_ratio

    def compute_partials(self, inputs, partials):
        lift_coeff = inputs['lift_coeff'].flatten()
        aspect_ratio = inputs['aspect_ratio'].flatten()
        oswald_efficiency = inputs['oswald_efficiency'].flatten()

        partials[
            'induced_drag_coeff',
            'lift_coeff'] = 2. * lift_coeff / np.pi / oswald_efficiency / aspect_ratio
        partials[
            'induced_drag_coeff',
            'aspect_ratio'] = -lift_coeff**2. / np.pi / oswald_efficiency / aspect_ratio**2.
        partials[
            'induced_drag_coeff',
            'oswald_efficiency'] = -lift_coeff**2. / np.pi / oswald_efficiency**2. / aspect_ratio


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('lift_coeff', np.random.random(shape))
    comp.add_output('aspect_ratio', np.random.random(shape))
    comp.add_output('oswald_efficiency', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = InducedDragCoeffComp(shape=shape, Q=1.)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
