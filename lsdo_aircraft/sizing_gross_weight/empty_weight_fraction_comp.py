from lsdo_utils.api import units, constants, ArrayExplicitComponent


lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

class EmptyWeightFractionComp(ArrayExplicitComponent):
    """
        This component computes the appropriate empty weight fraction based on the type of aircraft selected in 'run.py'. The options that are required for this component 
        are given in 'aircraft.py', and are defined based on the type of aircraft selected. The values for: 'a', 'c' and 'k_vs' are taken from the Raymer Empty Weight 
        Fraction Regression. The empty weight fraction is computed based on the input 'gross_weight'.
    """
    def array_initialize(self):
        self.options.declare('a', types=float)
        self.options.declare('c', types=float)
        self.options.declare('k_vs', types=float)

    def array_setup(self):
        self.array_add_input('gross_weight')
        self.array_add_output('empty_weight_fraction')
        self.array_declare_partials('empty_weight_fraction', 'gross_weight')

    def compute(self, inputs, outputs):
        a = self.options['a']
        c = self.options['c']
        k_vs = self.options['k_vs']

        gross_weight = inputs['gross_weight']

        outputs['empty_weight_fraction'] = a * lb_N ** c * gross_weight ** c * k_vs

    def compute_partials(self, inputs, partials):
        a = self.options['a']
        c = self.options['c']
        k_vs = self.options['k_vs']

        gross_weight = inputs['gross_weight'].flatten()

        partials['empty_weight_fraction', 'gross_weight'] = a * lb_N ** c * c * gross_weight ** (c - 1) * k_vs


if __name__ == '__main__':
    import numpy as np

    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)
    shape = (100,)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('gross_weight', 30000. * np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = EmptyWeightFractionComp(
        shape=shape,
        a=2.36,
        c=-0.18,
        k_vs=1.,
    )
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)

    