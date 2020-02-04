import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class ParasiticDragCoeffComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('Q', types=float)

    def array_setup(self):
        self.array_add_input('skin_friction_coeff')
        self.array_add_input('form_factor')
        self.array_add_output('parasitic_drag_coeff')

        self.array_declare_partials('parasitic_drag_coeff',
                                    'skin_friction_coeff')
        self.array_declare_partials('parasitic_drag_coeff', 'form_factor')

    def compute(self, inputs, outputs):
        Q = self.options['Q']

        skin_friction_coeff = inputs['skin_friction_coeff']
        form_factor = inputs['form_factor']

        outputs['parasitic_drag_coeff'] = skin_friction_coeff * form_factor * Q

    def compute_partials(self, inputs, partials):
        Q = self.options['Q']

        skin_friction_coeff = inputs['skin_friction_coeff'].flatten()
        form_factor = inputs['form_factor'].flatten()

        partials['parasitic_drag_coeff',
                 'skin_friction_coeff'] = form_factor * Q
        partials['parasitic_drag_coeff',
                 'form_factor'] = skin_friction_coeff * Q


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('skin_friction_coeff', np.random.random(shape))
    comp.add_output('form_factor', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = ParasiticDragCoeffComp(shape=shape, Q=1.)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
