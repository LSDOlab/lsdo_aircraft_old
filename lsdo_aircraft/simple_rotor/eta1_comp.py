import numpy as np

from lsdo_utils.api import BracketedImplicitComp, float_types


eps = 1.e-10

def get_res_func(options, inputs, eta1):
    blade_solidity = options['blade_solidity']

    power_coeff = inputs['power_coeff']
    advance_ratio = inputs['advance_ratio']
    blade_drag_coeff = inputs['blade_drag_coeff']
    glauert_factor = inputs['glauert_factor']

    eta2 = 1. - 4. / np.pi ** 3 * eta1 * power_coeff / advance_ratio
    eta3 = 1. - np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff * glauert_factor
    return 1 - eta1 - 2 / np.pi * power_coeff * eta2 * eta3 * eta1 ** 3 / advance_ratio ** 3


def get_derivs_func(options, inputs, eta1, partials):
    blade_solidity = options['blade_solidity']

    power_coeff = inputs['power_coeff'].flatten()
    advance_ratio = inputs['advance_ratio'].flatten()
    blade_drag_coeff = inputs['blade_drag_coeff'].flatten()
    glauert_factor = inputs['glauert_factor'].flatten()
    eta1 = eta1.flatten()

    eta2 = 1. - 4. / np.pi ** 3 * eta1 * power_coeff / advance_ratio
    eta3 = 1. - np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff * glauert_factor
    residuals = 1 - eta1 - 2 / np.pi * power_coeff * eta2 * eta3 * eta1 ** 3 / advance_ratio ** 3

    deta2_dpower_coeff = -4. / np.pi ** 3 * eta1 / advance_ratio
    deta2_dadvance_ratio = 4. / np.pi ** 3 * eta1 * power_coeff / advance_ratio ** 2
    deta2_deta1 = -4. / np.pi ** 3 * power_coeff / advance_ratio

    deta3_dpower_coeff = np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) ** 2 * blade_solidity * blade_drag_coeff * glauert_factor
    deta3_dblade_drag_coeff = -np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * glauert_factor
    deta3_dglauert_factor = -np.pi ** 4 / 8. * eta2 ** 2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff
    deta3_deta2 = -2 * np.pi ** 4 / 8. * eta2 / (power_coeff + eps) * blade_solidity * blade_drag_coeff * glauert_factor

    dres_deta1 = -1. - 2 / np.pi * power_coeff * eta2 * eta3 * 3 * eta1 ** 2 / advance_ratio ** 3
    dres_deta2 = -2 / np.pi * power_coeff * eta3 * eta1 ** 3 / advance_ratio ** 3
    dres_deta3 = -2 / np.pi * power_coeff * eta2 * eta1 ** 3 / advance_ratio ** 3
    dres_dpower_coeff = -2 / np.pi * eta2 * eta3 * eta1 ** 3 / advance_ratio ** 3
    dres_dadvance_ratio = 6. / np.pi * power_coeff * eta2 * eta3 * eta1 ** 3 / advance_ratio ** 4

    partials['eta1', 'eta1'] = dres_deta1 + dres_deta2 * deta2_deta1 + dres_deta3 * deta3_deta2 * deta2_deta1
    partials['eta1', 'power_coeff'] = dres_dpower_coeff + dres_deta3 * deta3_dpower_coeff + dres_deta2 * deta2_dpower_coeff + dres_deta3 * deta3_deta2 * deta2_dpower_coeff
    partials['eta1', 'advance_ratio'] = dres_dadvance_ratio + dres_deta2 * deta2_dadvance_ratio + dres_deta3 * deta3_deta2 * deta2_dadvance_ratio
    partials['eta1', 'blade_drag_coeff'] = dres_deta3 * deta3_dblade_drag_coeff
    partials['eta1', 'glauert_factor'] = dres_deta3 * deta3_dglauert_factor

    return dres_deta1 + dres_deta2 * deta2_deta1 + dres_deta3 * deta3_deta2 * deta2_deta1


class Eta1Comp(BracketedImplicitComp):

    def post_initialize(self):
        self.options.declare('blade_solidity', types=float_types)

    def pre_setup(self):
        self.options['out_name'] = 'eta1'
        self.options['in_names'] = [
            'power_coeff',
            'advance_ratio',
            'blade_drag_coeff',
            'glauert_factor',
        ]
        self.options['get_res_func'] = get_res_func
        self.options['get_derivs_func'] = get_derivs_func


if __name__ == '__main__':
    import numpy as np

    from openmdao.api import Problem, IndepVarComp


    blade_solidity = 0.2

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('eta2', np.random.random(shape))
    comp.add_output('eta3', np.random.random(shape))
    comp.add_output('power_coeff', np.random.random(shape))
    comp.add_output('advance_ratio', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = Eta1Comp(shape=shape, blade_solidity=blade_solidity)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)