from __future__ import division, print_function
import numpy as np

from lsdo_utils.comps.array_explicit_component import ArrayExplicitComponent
from lsdo_aircraft.aerodynamics.drag_utils import compute_Cf, compute_Cf_deriv, compute_Cf_coefficients

Re_trans = 5e5  #Laminar-turbulent transition
delta_Re = 5e4

Re_lam = Re_trans - delta_Re  #Laminar
Re_turb = Re_trans + delta_Re  #Turbulent

a3, a2, a1, a0 = compute_Cf_coefficients(Re_trans, delta_Re)


class SkinFrictionCoeffComp(ArrayExplicitComponent):
    def array_setup(self):
        self.Re_name = Re_name = 'reynolds_number'
        self.Cf_name = Cf_name = 'skin_friction_coeff'

        self.array_add_input(Re_name)
        self.array_add_output(Cf_name)

        self.array_declare_partials(Cf_name, Re_name)

    def compute(self, inputs, outputs):
        Re = inputs[self.Re_name]

        outputs[self.Cf_name] = compute_Cf(a3, a2, a1, a0, Re_lam, Re_turb, Re)

    def compute_partials(self, inputs, partials):
        Re = inputs[self.Re_name]

        partials[self.Cf_name,
                 self.Re_name] = compute_Cf_deriv(a3, a2, a1, a0, Re_lam,
                                                  Re_turb, Re).flatten()


if __name__ == '__main__':
    from openmdao.api import Problem, IndepVarComp

    shape = (2, 3)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('reynolds_number', val=np.random.random(shape))
    prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

    comp = SkinFrictionCoeffComp(shape=shape)
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup()
    prob.run_model()
    prob.check_partials(compact_print=True)
