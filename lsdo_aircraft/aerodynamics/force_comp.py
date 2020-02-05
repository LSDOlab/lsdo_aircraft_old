from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class ForceComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('coeff_name', types=str)
        self.options.declare('force_name', types=str)
        self.options.declare('area_name', default='area', types=str)

    def array_setup(self):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        self.array_add_input(coeff_name)
        self.array_add_input('density')
        self.array_add_input('speed')
        self.array_add_input(area_name)
        self.array_add_output(force_name)

        self.array_declare_partials(force_name, '*')

    def compute(self, inputs, outputs):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        coeff = inputs[coeff_name]
        density = inputs['density']
        speed = inputs['speed']
        area = inputs[area_name]

        outputs[force_name] = coeff * 0.5 * density * speed**2 * area

    def compute_partials(self, inputs, partials):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        coeff = inputs[coeff_name].flatten()
        density = inputs['density'].flatten()
        speed = inputs['speed'].flatten()
        area = inputs[area_name].flatten()

        partials[force_name, coeff_name] = 0.5 * density * speed**2 * area
        partials[force_name, 'density'] = coeff * 0.5 * speed**2 * area
        partials[force_name, 'speed'] = coeff * density * speed * area
        partials[force_name, area_name] = coeff * 0.5 * density * speed**2


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    coeff_name = 'lift_coeff'
    force_name = 'lift'

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output(coeff_name, np.random.random(shape))
    comp.add_output('density', np.random.random(shape))
    comp.add_output('speed', np.random.random(shape))
    comp.add_output('area', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = ForceComp(shape=shape, coeff_name=coeff_name, force_name=force_name)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
