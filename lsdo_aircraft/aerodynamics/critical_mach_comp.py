import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class CriticalMachComp(ArrayExplicitComponent):
    def initialize(self):
        self.options.declare('shape')
        self.options.declare('tech_factor', default=0.87)

    def array_setup(self):
        self.array_add_input('lift_coeff')
        self.array_add_input('t_c')
        self.array_add_output('critical_mach')

        self.array_declare_partials('critical_mach', 't_c')
        self.array_declare_partials('critical_mach', 'lift_coeff')

    def compute(self, inputs, outputs):
        tech_factor = self.options['tech_factor']
        CL = inputs['lift_coeff']
        t_c = inputs['t_c']
        drag_div_mach = tech_factor - 0.1 * CL - t_c
        outputs['critical_mach'] = drag_div_mach - 0.1077

    def compute_partials(self, inputs, partials):
        partials['critical_mach', 't_c'] = -1
        partials['critical_mach', 'lift_coeff'] = -0.1


if __name__ == '__main__':
    import numpy as np
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('lift_coeff', np.random.random(shape))
    comp.add_output('t_c', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = CriticalMachComp(shape=shape, tech_factor=0.87)
    prob.model.add_subsystem('sub', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)

    prob = Problem()

    comp = CriticalMachComp(shape=shape, tech_factor=0.95)
    prob.model.add_subsystem('super', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
