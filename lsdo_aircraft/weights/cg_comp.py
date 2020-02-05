from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class CGComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('weight_names', types=list)
        self.options.declare('cg_names', types=list)

    def array_setup(self):
        weight_names = self.options['weight_names']
        cg_names = self.options['cg_names']

        self.array_add_input('gross_weight')

        for weight_name, cg_name in zip(weight_names, cg_names):
            self.array_add_input(weight_name)
            self.array_add_input(cg_name)

        self.array_add_output('cg')

        self.array_declare_partials('*', '*')

    def compute(self, inputs, outputs):
        weight_names = self.options['weight_names']
        cg_names = self.options['cg_names']

        outputs['cg'] = 0.
        for weight_name, cg_name in zip(weight_names, cg_names):
            outputs['cg'] += inputs[weight_name] * inputs[cg_name] / inputs[
                'gross_weight']

    def compute_partials(self, inputs, partials):
        weight_names = self.options['weight_names']
        cg_names = self.options['cg_names']

        partials['cg', 'gross_weight'] = 0.
        for weight_name, cg_name in zip(weight_names, cg_names):
            partials['cg',
                     'gross_weight'] -= (inputs[weight_name] *
                                         inputs[cg_name] /
                                         inputs['gross_weight']**2).flatten()
            partials['cg', weight_name] = (inputs[cg_name] /
                                           inputs['gross_weight']).flatten()
            partials['cg', cg_name] = (inputs[weight_name] /
                                       inputs['gross_weight']).flatten()


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    cg_names = ['cg1', 'cg2', 'cg3']
    weight_names = ['W1', 'W2', 'W3']

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('gross_weight', val=np.random.random(shape))
    for weight_name, cg_name in zip(weight_names, cg_names):
        comp.add_output(weight_name, val=np.random.random(shape))
        comp.add_output(cg_name, val=np.random.random(shape))
    prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

    comp = CGComp(shape=shape, cg_names=cg_names, weight_names=weight_names)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup()
    prob.run_model()
    prob.check_partials(compact_print=True)
