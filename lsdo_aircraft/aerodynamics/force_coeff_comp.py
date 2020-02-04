from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class ForceCoeffComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('coeff_name', types=str)
        self.options.declare('force_name', types=str)
        self.options.declare('area_name', default='area', types=str)

    def array_setup(self):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        self.array_add_input(force_name)
        self.array_add_input('density')
        self.array_add_input('speed')
        self.array_add_input(area_name)
        self.array_add_output(coeff_name)

        self.array_declare_partials(coeff_name, '*')

    def compute(self, inputs, outputs):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        force = inputs[force_name]
        density = inputs['density']
        speed = inputs['speed']
        area = inputs[area_name]

        outputs[coeff_name] = force / 0.5 / density / speed**2 / area

    def compute_partials(self, inputs, partials):
        coeff_name = self.options['coeff_name']
        force_name = self.options['force_name']
        area_name = self.options['area_name']

        force = inputs[force_name].flatten()
        density = inputs['density'].flatten()
        speed = inputs['speed'].flatten()
        area = inputs[area_name].flatten()

        partials[coeff_name, force_name] = 1. / 0.5 / density / speed**2 / area
        partials[coeff_name,
                 'density'] = -force / 0.5 / density**2 / speed**2 / area
        partials[coeff_name,
                 'speed'] = -2 * force / 0.5 / density / speed**3 / area
        partials[coeff_name,
                 area_name] = -force / 0.5 / density / speed**2 / area**2


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    coeff_name = 'lift_coeff'
    force_name = 'lift'

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output(force_name, np.random.random(shape))
    comp.add_output('density', np.random.random(shape))
    comp.add_output('speed', np.random.random(shape))
    comp.add_output('area', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = ForceCoeffComp(shape=shape,
                          coeff_name=coeff_name,
                          force_name=force_name)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
