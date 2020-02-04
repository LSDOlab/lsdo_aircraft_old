from __future__ import print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent

lb_to_N = 1.0 / 2.2 * 9.81
deg_rad = np.pi / 180.


class WingWeightComp(ArrayExplicitComponent):
    def array_initialize(self):
        self.options.declare('lifting_surface')

    def array_setup(self):
        self.area_name = area_name = 'area'
        self.aspect_ratio_name = aspect_ratio_name = 'aspect_ratio'
        self.dynamic_pressure_name = dynamic_pressure_name = 'max_dynamic_pressure'
        self.taper_ratio_name = taper_ratio_name = 'taper_ratio'
        self.sweep_name = sweep_name = 'sweep_deg'
        self.gross_weight_name = gross_weight_name = 'gross_weight'
        self.weight_name = weight_name = 'weight'

        self.array_add_input(area_name, val=1.0)
        self.array_add_input(aspect_ratio_name, val=1.0)
        self.array_add_input(dynamic_pressure_name, val=1.0)
        self.array_add_input(taper_ratio_name, val=1.0)
        self.array_add_input(sweep_name, val=1.0)
        self.array_add_input(gross_weight_name, val=30e3)
        self.array_add_output(weight_name, val=1.0)

        self.array_declare_partials(weight_name, area_name)
        self.array_declare_partials(weight_name, aspect_ratio_name)
        self.array_declare_partials(weight_name, dynamic_pressure_name)
        self.array_declare_partials(weight_name, taper_ratio_name)
        self.array_declare_partials(weight_name, sweep_name)
        self.array_declare_partials(weight_name, gross_weight_name)

    def compute(self, inputs, outputs):
        # Mult_f = lifting_surface_dict.settings['multiplicative_correction']
        Mult_f = 0.61
        Add_f = -330.

        Mult_f = self.options['lifting_surface']['multiplicative_factor']
        Add_f = self.options['lifting_surface']['additive_factor']

        tc = .17
        # Nz : ultimate load factor
        Nz = 6.6
        Sw = inputs[self.area_name] * 10.7639  # m2 to ft2
        AR = inputs[self.aspect_ratio_name]
        q = inputs[self.dynamic_pressure_name] * 0.02088  # N/m2 to lb/ft2
        l = inputs[self.taper_ratio_name]
        A = inputs[self.sweep_name] * deg_rad
        Wdg = inputs[self.gross_weight_name] * 0.224261  # N to lb

        outputs[
            self.weight_name] = (0.036 * Sw**0.758 *
                                 (AR /
                                  (np.cos(A))**2)**0.6 * q**0.006 * l**0.04 *
                                 (100 * tc / np.cos(A))**-0.3 *
                                 (Nz * Wdg)**0.49) * lb_to_N * Mult_f + Add_f

    def compute_partials(self, inputs, J):
        # Mult_f = lifting_surface_dict.settings['multiplicative_correction']
        Mult_f = 0.61
        Add_f = -330.

        Mult_f = self.options['lifting_surface']['multiplicative_factor']
        Add_f = self.options['lifting_surface']['additive_factor']

        tc = .17
        Nz = 6.6
        Sw = inputs[self.area_name].flatten() * 10.7639  # m2 to ft2
        AR = inputs[self.aspect_ratio_name].flatten()
        q = inputs[
            self.dynamic_pressure_name].flatten() * 0.02088  # N/m2 to lb/ft2
        l = inputs[self.taper_ratio_name].flatten()
        A = inputs[self.sweep_name].flatten() * deg_rad
        Wdg = inputs[self.gross_weight_name].flatten() * 0.224261  # N to lb

        J[self.weight_name,
          self.area_name] = (0.036 * 0.758 * 10.7639 * Sw**(-0.242) *
                             (AR / (np.cos(A))**2)**0.6 * q**0.006 * l**0.04 *
                             (100 * tc / np.cos(A))**-0.3 *
                             (Nz * Wdg)**0.49) * lb_to_N * Mult_f

        #= 0.036*0.758*Sw**(-0.242)*(AR/(np.cos(A))**2)**0.6*q**0.006*l**0.04*(100*tc/np.cos(A))**-0.3*(Nz*Wdg)**0.49

        J[self.weight_name,
          self.aspect_ratio_name] = (0.036 * 0.6 * Sw**0.758 * AR**(-0.4) *
                                     (1 / (np.cos(A))**2)**0.6 * q**0.006 *
                                     l**0.04 * (100 * tc / np.cos(A))**-0.3 *
                                     (Nz * Wdg)**0.49) * lb_to_N * Mult_f

        J[self.weight_name,
          self.dynamic_pressure_name] = (0.036 * Sw**0.758 *
                                         (AR / (np.cos(A))**2)**0.6 * 0.006 *
                                         0.02088 * q**(-0.994) * l**0.04 *
                                         (100 * tc / np.cos(A))**-0.3 *
                                         (Nz * Wdg)**0.49) * lb_to_N * Mult_f

        J[self.weight_name, self.gross_weight_name] = (
            0.036 * Sw**0.758 * (AR /
                                 (np.cos(A))**2)**0.6 * q**0.006 * l**0.04 *
            (100 * tc / np.cos(A))**-0.3 * Nz**0.49 * 0.224261 * 0.49 *
            Wdg**(-0.51)) * lb_to_N * Mult_f

        J[self.weight_name,
          self.taper_ratio_name] = (0.036 * Sw**0.758 * (AR /
                                                         (np.cos(A))**2)**0.6 *
                                    q**0.006 * 0.04 * l**(-0.96) *
                                    (100 * tc / np.cos(A))**-0.3 *
                                    (Nz * Wdg)**0.49) * lb_to_N * Mult_f

        J[self.weight_name, self.sweep_name] = (
            0.036*Sw**0.758*AR**0.6 \
            *(-1.2)*np.cos(A)**(-2.2)*-np.sin(A) \
            *q**0.006*l**0.04*(100*tc/np.cos(A))**-0.3*(Nz*Wdg)**0.49 * deg_rad \
            + 0.036*Sw**0.758*(AR/(np.cos(A))**2)**0.6 \
            *q**0.006*l**0.04*(100*tc)**(-0.3) \
            *0.3*np.cos(A)**(-0.7)*(-np.sin(A)) \
            *(Nz*Wdg)**0.49 * deg_rad
        ) * lb_to_N * Mult_f


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('area', np.random.random(shape))
    comp.add_output('aspect_ratio', np.random.random(shape))
    comp.add_output('dynamic_pressure', np.random.random(shape))
    comp.add_output('taper_ratio', np.random.random(shape))
    comp.add_output('sweep_deg', np.random.random(shape))
    comp.add_output('gross_weight', np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = WingWeightComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.check_partials(compact_print=True)