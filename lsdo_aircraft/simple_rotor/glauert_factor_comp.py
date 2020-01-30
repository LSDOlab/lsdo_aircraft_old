import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class GlauertFactorComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('flow_angle')
        self.array_add_output('glauert_factor')

        self.array_declare_partials('glauert_factor', 'flow_angle')

    def compute(self, inputs, outputs):
        flow_angle = inputs['flow_angle']

        cos = np.cos(flow_angle)
        tan = np.tan(flow_angle)

        outputs['glauert_factor'] = (
            1. / 8. / cos * (2 + 5 * tan ** 2) -
            3. / 16. * tan ** 4 * np.log( (1 - cos) / (1 + cos) )
        )

    def compute_partials(self, inputs, partials):
        flow_angle = inputs['flow_angle'].flatten()

        sin = np.sin(flow_angle)
        cos = np.cos(flow_angle)
        tan = np.tan(flow_angle)
        
        partials['glauert_factor', 'flow_angle'] = (
            1. / 8. * sin / cos ** 2 * (2 + 5 * tan ** 2) +
            1. / 8. / cos * 10 * tan / cos ** 2 -
            3. / 4. * tan ** 3 / cos ** 2 * np.log( (1 - cos) / (1 + cos) ) -
            3. / 16. * tan ** 4 * ( (1 + cos) / (1 - cos) ) * (
                sin * (1 + cos) - (1 - cos) * -sin
            ) / (1 + cos) ** 2
        )


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('flow_angle', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = GlauertFactorComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)