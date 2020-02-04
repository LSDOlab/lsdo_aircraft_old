from __future__ import division, print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class LiftingSurfaceFFComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('x_c_max_camber', types=float)
        self.options.declare('t_c', types=float)

    def array_setup(self):
        x_c_max_camber = self.options['x_c_max_camber']
        t_c = self.options['t_c']

        self.factor = 1. + 0.6 / x_c_max_camber * t_c + 100. * t_c**4

        self.array_add_input('mach_number')
        self.array_add_input('sweep')
        self.array_add_output('form_factor')

        self.array_declare_partials('form_factor', 'mach_number')
        self.array_declare_partials('form_factor', 'sweep')

    def compute(self, inputs, outputs):
        mach_number = inputs['mach_number']
        sweep = inputs['sweep']

        outputs[
            'form_factor'] = self.factor * 1.34 * mach_number**0.18 * np.cos(
                sweep)**0.28

    def compute_partials(self, inputs, partials):
        mach_number = inputs['mach_number'].flatten()
        sweep = inputs['sweep'].flatten()

        partials[
            'form_factor',
            'mach_number'] = self.factor * 1.34 * 0.18 * mach_number**-0.82 * np.cos(
                sweep)**0.28
        partials[
            'form_factor',
            'sweep'] = self.factor * 1.34 * mach_number**0.18 * 0.28 * np.cos(
                sweep)**-0.72 * -np.sin(sweep)


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('mach_number', val=np.random.random(shape))
    comp.add_output('sweep', val=np.random.random(shape))
    prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

    comp = LiftingSurfaceFFComp(shape=shape, x_c_max_camber=0.3, t_c=0.12)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup()
    prob.run_model()
    prob.check_partials(compact_print=True)
