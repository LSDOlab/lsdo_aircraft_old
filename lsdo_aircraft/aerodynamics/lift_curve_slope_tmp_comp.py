import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent


class LiftCurveSlopeTmpComp(ArrayExplicitComponent):
    def array_setup(self):
        self.array_add_input('aspect_ratio')
        self.array_add_input('mach_number')
        self.array_add_input('sweep')
        self.array_add_output('lift_curve_slope_tmp')

        self.array_declare_partials('lift_curve_slope_tmp', 'aspect_ratio')
        self.array_declare_partials('lift_curve_slope_tmp', 'mach_number')
        self.array_declare_partials('lift_curve_slope_tmp', 'sweep')

    def compute(self, inputs, outputs):
        aspect_ratio = inputs['aspect_ratio']
        mach_number = inputs['mach_number']
        sweep = inputs['sweep']

        outputs['lift_curve_slope_tmp'] = (4. + aspect_ratio**2 *
                                           (1 - mach_number**2) *
                                           (1 + np.tan(sweep)**2 /
                                            (1 - mach_number**2)))

    def compute_partials(self, inputs, partials):
        aspect_ratio = inputs['aspect_ratio'].flatten()
        mach_number = inputs['mach_number'].flatten()
        sweep = inputs['sweep'].flatten()

        partials['lift_curve_slope_tmp',
                 'aspect_ratio'] = (2. * aspect_ratio * (1 - mach_number**2) *
                                    (1 + np.tan(sweep)**2 /
                                     (1 - mach_number**2)))
        partials['lift_curve_slope_tmp',
                 'mach_number'] = ((aspect_ratio**2 *
                                    (1 + np.tan(sweep)**2 /
                                     (1 - mach_number**2)) + aspect_ratio**2 *
                                    (1 - mach_number**2) *
                                    (-np.tan(sweep)**2 /
                                     (1 - mach_number**2)**2)) * -2 *
                                   mach_number)
        partials['lift_curve_slope_tmp',
                 'sweep'] = (aspect_ratio**2 * (1 - mach_number**2) *
                             (2 * np.tan(sweep) / np.cos(sweep)**2 /
                              (1 - mach_number**2)))


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('aspect_ratio', np.random.random(shape))
    comp.add_output('mach_number', np.random.random(shape))
    comp.add_output('sweep', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = LiftCurveSlopeTmpComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)
