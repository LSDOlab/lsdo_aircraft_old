import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class FlowAngleComp(ArrayExplicitComponent):

    def array_setup(self):
        self.array_add_input('tip_speed')
        self.array_add_input('speed')
        self.array_add_output('flow_angle')

        self.array_declare_partials('flow_angle', 'tip_speed')
        self.array_declare_partials('flow_angle', 'speed')

    def compute(self, inputs, outputs):
        outputs['flow_angle'] = np.arctan2(inputs['speed'], inputs['tip_speed'])

    def compute_partials(self, inputs, partials):
        partials['flow_angle', 'tip_speed'] = (
            -inputs['speed'] / ( inputs['tip_speed'] ** 2 + inputs['speed'] ** 2 )
        ).flatten()
        partials['flow_angle', 'speed'] = (
            inputs['tip_speed'] / ( inputs['tip_speed'] ** 2 + inputs['speed'] ** 2 )
        ).flatten()


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('tip_speed', np.random.random(shape))
    comp.add_output('speed', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = FlowAngleComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)