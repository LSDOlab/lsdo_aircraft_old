import numpy as np

from lsdo_utils.api import ArrayExplicitComponent, float_types


class LiftCurveSlopeDenominatorComp(ArrayExplicitComponent):

    def array_initialize(self):
        self.options.declare('lift_curve_slope_2D', types=float_types)
        self.options.declare('wing_exposed_ratio', types=float_types)
        self.options.declare('fuselage_diameter_span', types=float_types)

    def array_setup(self):
        fuselage_diameter_span = self.options['fuselage_diameter_span']
        wing_exposed_ratio = self.options['wing_exposed_ratio']

        self.array_add_input('aspect_ratio')
        self.array_add_input('mach_number')
        self.array_add_input('sweep')
        self.array_add_output('lift_curve_slope_denominator')

        self.array_declare_partials('lift_curve_slope_denominator', 'aspect_ratio')
        self.array_declare_partials('lift_curve_slope_denominator', 'mach_number')
        self.array_declare_partials('lift_curve_slope_denominator', 'sweep')

        self.S_F = wing_exposed_ratio * 1.07 * (1 + fuselage_diameter_span) ** 2

    def compute(self, inputs, outputs):
        lift_curve_slope_2D = self.options['lift_curve_slope_2D']

        aspect_ratio = inputs['aspect_ratio']
        mach_number = inputs['mach_number']
        sweep = inputs['sweep']

        beta = np.sqrt(1 - mach_number ** 2)
        eta = lift_curve_slope_2D / (2 * np.pi) * beta

        arg = 4. + aspect_ratio ** 2 * beta ** 2 / eta ** 2 * \
            ( 1 + np.tan(sweep) ** 2 / beta ** 2 )

        outputs['lift_curve_slope_denominator'] = 2 + np.sqrt(arg)

    def compute_partials(self, inputs, partials):
        lift_curve_slope_2D = self.options['lift_curve_slope_2D']

        aspect_ratio = inputs['aspect_ratio'].flatten()
        mach_number = inputs['mach_number'].flatten()
        sweep = inputs['sweep'].flatten()

        beta = np.sqrt(1 - mach_number ** 2)
        eta = lift_curve_slope_2D / (2 * np.pi) * beta

        dbeta_dmach_number = -mach_number / np.sqrt(1 - mach_number ** 2)
        deta_dbeta = lift_curve_slope_2D / (2 * np.pi)

        arg = 4. + aspect_ratio ** 2 * beta ** 2 / eta ** 2 * \
            ( 1 + np.tan(sweep) ** 2 / beta ** 2 )

        darg_daspect_ratio = 2 * aspect_ratio * beta ** 2 / eta ** 2 * \
            ( 1 + np.tan(sweep) ** 2 / beta ** 2 )
        darg_dbeta = aspect_ratio ** 2 * 2 * beta / eta ** 2 * \
            ( 1 + np.tan(sweep) ** 2 / beta ** 2 ) + aspect_ratio ** 2 * beta ** 2 / eta ** 2 * \
            ( -2. * np.tan(sweep) ** 2 / beta ** 3 )
        darg_deta = aspect_ratio ** 2 * beta ** 2 * -2. / eta ** 3 * \
            ( 1 + np.tan(sweep) ** 2 / beta ** 2 )
        darg_dsweep = aspect_ratio ** 2 * beta ** 2 / eta ** 2 * \
            ( 2 * np.tan(sweep) / np.cos(sweep) ** 2 / beta ** 2 )

        partials['lift_curve_slope_denominator', 'aspect_ratio'] = 0.5 / np.sqrt(arg) * (
            darg_daspect_ratio
        )
        partials['lift_curve_slope_denominator', 'mach_number'] = 0.5 / np.sqrt(arg) * (
            darg_deta * deta_dbeta * dbeta_dmach_number + darg_dbeta * dbeta_dmach_number
        )
        partials['lift_curve_slope_denominator', 'sweep'] = 0.5 / np.sqrt(arg) * (
            darg_dsweep
        )


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp


    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('aspect_ratio', np.random.random(shape))
    comp.add_output('mach_number', np.random.random(shape))
    comp.add_output('sweep', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = LiftCurveSlopeDenominatorComp(
        shape=shape,
        lift_curve_slope_2D=2 * np.pi,
        wing_exposed_ratio=0.9,
        fuselage_diameter_span=0.1,
    )
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)