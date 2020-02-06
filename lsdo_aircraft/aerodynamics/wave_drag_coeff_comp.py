import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class WaveDragCoeffComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('mach_number')
        self.array_add_input('critical_mach_number')
        self.array_add_output('wave_drag_coeff')

        self.array_declare_partials('wave_drag_coeff', 'mach_number')
        self.array_declare_partials('wave_drag_coeff', 'critical_mach_number')

    def compute(self, inputs, outputs):
        d_mach = inputs['mach_number'] - inputs['critical_mach_number']
        d_mach *= d_mach > 0.

        outputs['wave_drag_coeff'] = 20. * d_mach ** 4

    def compute_partials(self, inputs, partials):
        d_mach = (inputs['mach_number'] - inputs['critical_mach_number']).flatten()
        d_mach *= d_mach > 0.

        partials['wave_drag_coeff', 'mach_number'] = 80. * d_mach ** 3
        partials['wave_drag_coeff', 'critical_mach_number'] = -80. * d_mach ** 3


if __name__ == '__main__':
    import numpy as np
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('mach_number', 10 * np.random.random(shape))
    comp.add_output('critical_mach_number', 10 * np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = WaveDragCoeffComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
    prob.model.list_outputs()