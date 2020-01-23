from lsdo_utils.api import units, constants, ArrayExplicitComponent
import numpy as np


class BreguetPropellantWeightFractionComp(ArrayExplicitComponent):
    """
        This component computes the propellant weight fraction from the Breguet range equation. 
        The inputs for this component are:
                    - lift to drag ratio 
                    - range_km (The range of flight in kilometers)
                    - cruise speed (In meters/second)
                    - tsfc (Thrust Specific Fuel Consumption)
            
        All of the values above are assumed to be in SI units, unless otherwise denoted. 

    """

    def array_initialize(self):
        pass

    def array_setup(self):
        self.array_add_input('lift_to_drag_ratio')
        self.array_add_input('range_km')
        self.array_add_input('cruise_speed')
        self.array_add_input('tsfc')
        self.array_add_output('propellant_weight_fraction')
        self.array_declare_partials('propellant_weight_fraction', 'lift_to_drag_ratio')
        self.array_declare_partials('propellant_weight_fraction', 'range_km')
        self.array_declare_partials('propellant_weight_fraction', 'cruise_speed')
        self.array_declare_partials('propellant_weight_fraction', 'tsfc')

    def compute(self, inputs, outputs):
        lift_to_drag_ratio = inputs['lift_to_drag_ratio']
        range_ = inputs['range_km'] * 1e3
        cruise_speed = inputs['cruise_speed']
        tsfc = inputs['tsfc']

        outputs['propellant_weight_fraction'] = 1 - np.exp(-range_ * tsfc / (cruise_speed * lift_to_drag_ratio))

    def compute_partials(self, inputs, partials):
        lift_to_drag_ratio = inputs['lift_to_drag_ratio'].flatten()
        range_ = inputs['range_km'].flatten() * 1e3
        cruise_speed = inputs['cruise_speed'].flatten()
        tsfc = inputs['tsfc'].flatten()
        
        partials['propellant_weight_fraction', 'cruise_speed'] = -1 * range_ * tsfc / ((cruise_speed ** 2) * lift_to_drag_ratio) * np.exp(-range_ * tsfc / (cruise_speed * lift_to_drag_ratio)) 
        partials['propellant_weight_fraction', 'tsfc'] =  range_ / (cruise_speed * lift_to_drag_ratio) * np.exp(-range_ * tsfc / (cruise_speed * lift_to_drag_ratio)) 
        partials['propellant_weight_fraction', 'lift_to_drag_ratio'] =  -1 * range_ * tsfc / (cruise_speed * (lift_to_drag_ratio ** 2)) * np.exp(-range_ * tsfc / (cruise_speed * lift_to_drag_ratio)) 
        partials['propellant_weight_fraction', 'range_km'] =  tsfc / (cruise_speed * lift_to_drag_ratio) * np.exp(-range_ * tsfc / (cruise_speed * lift_to_drag_ratio)) * 1e3


if __name__ == '__main__':
    import numpy as np

    from openmdao.api import Problem, IndepVarComp


    shape = (20, 30)
    shape = (2, 3)
    # shape = (100,)

    prob = Problem()

    comp = IndepVarComp()
    comp.add_output('cruise_speed', 100. * np.random.random(shape))
    comp.add_output('tsfc', 1.e-4 * np.random.random(shape))
    comp.add_output('lift_to_drag_ratio', 17. * np.random.random(shape))
    comp.add_output('range_km', 5000 * np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = BreguetPropellantWeightFractionComp(
        shape=shape,   
    )
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.model.list_outputs()
    prob.check_partials(compact_print=True)

