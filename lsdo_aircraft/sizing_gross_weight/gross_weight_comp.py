import numpy as np

from lsdo_utils.api import units, constants

from openmdao.api import ImplicitComponent


eps = 1.e-10

lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

class GrossWeightComp(ImplicitComponent):
    """
        This component solves for the gross weight of the aircraft selected by solving a non-linear equation. The options that are required for this component are given in 'aircraft.py', 
        and are defined based on the type of aircraft selected. The values for: 'a', 'c' and 'k_vs' are taken from the Raymer Empty Weight Fraction Regression. Other options are 'shape', 
        'num_iter' (maximum number of iterations), and 'weight_max' (limit on gross weight).
    """

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('a', types=float)
        self.options.declare('c', types=float)
        self.options.declare('k_vs', types=float)
        self.options.declare('weight_max', default=1.e8, types=float)
        self.options.declare('num_iter', default=100, types=int)

    def setup(self):
        shape = self.options['shape']

        self.add_input('fixed_weight', shape=shape)
        self.add_input('propellant_weight_fraction', shape=shape)
        self.add_output('gross_weight', shape=shape)

        arange = np.arange(np.prod(shape))

        self.declare_partials('gross_weight', '*', rows=arange, cols=arange)

    def get_res(self, inputs, gross_weight):
        a = self.options['a']
        c = self.options['c']
        k_vs = self.options['k_vs']

        fixed_weight = inputs['fixed_weight']
        propellant_weight_fraction = inputs['propellant_weight_fraction']

        residual = fixed_weight + a * lb_N ** c * gross_weight ** (c + 1.) * k_vs + (propellant_weight_fraction - 1.) * gross_weight
        
        return residual

    def get_derivs(self, inputs, gross_weight):
        a = self.options['a']
        c = self.options['c']
        k_vs = self.options['k_vs']

        fixed_weight = inputs['fixed_weight'].flatten()
        propellant_weight_fraction = inputs['propellant_weight_fraction'].flatten()

        # residual = fixed_weight + a * lb_N ** c * gross_weight ** (c + 1.) * k_vs + (propellant_weight_fraction - 1.) * gross_weight

        dres_dfixed = 1.
        dres_dpwf = gross_weight
        dres_dgw = a * lb_N ** c * (c + 1.) * gross_weight ** c * k_vs + (propellant_weight_fraction - 1.)
        
        return dres_dfixed, dres_dpwf, dres_dgw

    def apply_nonlinear(self, inputs, outputs, residuals):        
        residuals['gross_weight'] = self.get_res(inputs, outputs['gross_weight'])

    def solve_nonlinear(self, inputs, outputs):
        weight_max = self.options['weight_max']
        num_iter = self.options['num_iter']

        gross_weight = outputs['gross_weight']

        xp = np.zeros(self.options['shape'])
        xn = weight_max * np.ones(self.options['shape'])

        for ind in range(num_iter):
            x = 0.5 * xp + 0.5 * xn
            r = self.get_res(inputs, x)
            mask_p = r >= 0
            mask_n = r < 0
            xp[mask_p] = x[mask_p]
            xn[mask_n] = x[mask_n]

            print(np.linalg.norm(r))

        outputs['gross_weight'] = 0.5 * xp + 0.5 * xn

    def linearize(self, inputs, outputs, partials):
        dres_dfixed, dres_dpwf, dres_dgw = self.get_derivs(inputs, outputs['gross_weight'].flatten())

        partials['gross_weight', 'fixed_weight'] = dres_dfixed
        partials['gross_weight', 'propellant_weight_fraction'] = dres_dpwf
        partials['gross_weight', 'gross_weight'] = dres_dgw

        self.jac = dres_dgw

    def solve_linear(self, d_outputs, d_residuals, mode):
        if mode == 'fwd':
            d_outputs['gross_weight'] += 1. / self.jac * d_residuals['gross_weight']
        else:
            d_residuals['gross_weight'] += 1. / self.jac * d_outputs['gross_weight']


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)
    shape = (100,)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('fixed_weight', 1000. * np.random.random(shape))
    comp.add_output('propellant_weight_fraction', 0.25 * np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = GrossWeightComp(
        shape=shape,
        a=2.36,
        c=-0.18,
        k_vs=1.,
        weight_max=1.e8,
        num_iter=100,
    )
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)

    