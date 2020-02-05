import numpy as np

from openmdao.api import ExplicitComponent


class Max2Comp(ExplicitComponent):

    def initialize(self):
        self.options.declare('in1_name', types=str)
        self.options.declare('in2_name', types=str)
        self.options.declare('out_name', types=str)
        self.options.declare('rho', types=float)

    def setup(self):
        in1_name = self.options['in1_name']
        in2_name = self.options['in2_name']
        out_name = self.options['out_name']

        self.add_input(in1_name)
        self.add_input(in2_name)
        self.add_output(out_name)

        self.declare_partials('*', '*')

    def compute(self, inputs, outputs):
        in1_name = self.options['in1_name']
        in2_name = self.options['in2_name']
        out_name = self.options['out_name']

        rho = self.options['rho']

        fmax = max(inputs[in1_name], inputs[in2_name])

        outputs[out_name] = fmax + 1. / rho * np.log(
            np.exp(rho * (inputs[in1_name] - fmax)) + np.exp(rho * (inputs[in2_name] - fmax))
        )

    def compute_partials(self, inputs, partials):
        in1_name = self.options['in1_name']
        in2_name = self.options['in2_name']
        out_name = self.options['out_name']

        rho = self.options['rho']

        fmax = max(inputs[in1_name], inputs[in2_name])

        partials[out_name, in1_name] = 1. / (
            np.exp(rho * (inputs[in1_name] - fmax)) + np.exp(rho * (inputs[in2_name] - fmax))
        ) * np.exp(rho * (inputs[in1_name] - fmax))

        partials[out_name, in2_name] = 1. / (
            np.exp(rho * (inputs[in1_name] - fmax)) + np.exp(rho * (inputs[in2_name] - fmax))
        ) * np.exp(rho * (inputs[in2_name] - fmax))


if __name__ == '__main__':
    from openmdao.api import Problem, Group, IndepVarComp


    in1 = 10.
    in2 = 12.
    rho = 20.

    prob = Problem()

    model = Group()

    comp = IndepVarComp()
    comp.add_output('in1', in1)
    comp.add_output('in2', in2)
    model.add_subsystem('ivc', comp, promotes=['*'])

    comp = Max2Comp(in1_name='in1', in2_name='in2', out_name='out', rho=rho)
    model.add_subsystem('comp', comp, promotes=['*'])

    prob.model = model
    prob.setup()
    prob.run_model()
    prob.check_partials(compact_print=True)

    for var_name in ['in1', 'in2', 'out']:
        print(var_name, prob[var_name])