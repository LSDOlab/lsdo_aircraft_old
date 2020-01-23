from lsdo_utils.api import units, constants, ArrayExplicitComponent
import numpy as np


class BreguetRangeComp(ArrayExplicitComponent):

    """
        This component computes the range of flight in kilometers using the Breguet Range Equation. 
        The inputs for this component are:
                    - lift to drag ratio 
                    - propellant to weight fraction 
                    - cruise speed (In meters/second)
                    - tsfc (Thrust Specific Fuel Consumption)
            
        All of the values above are assumed to be in SI units, unless otherwise denoted. 

    
    """

    def array_initialize(self):
        pass

    def array_setup(self):
        self.array_add_input('lift_to_drag_ratio')
        self.array_add_input('propellant_weight_fraction')
        self.array_add_input('cruise_speed')
        self.array_add_input('tsfc')
        self.array_add_output('range_km')
        self.array_declare_partials('range_km', 'lift_to_drag_ratio')
        self.array_declare_partials('range_km', 'propellant_weight_fraction')
        self.array_declare_partials('range_km', 'cruise_speed')
        self.array_declare_partials('range_km', 'tsfc')

    def compute(self, inputs, outputs):
        lift_to_drag_ratio = inputs['lift_to_drag_ratio']
        propellant_weight_fraction = inputs['propellant_weight_fraction']
        cruise_speed = inputs['cruise_speed']
        tsfc = inputs['tsfc']

        outputs['range_km'] = -(cruise_speed / tsfc) * lift_to_drag_ratio * np.log(1 - propellant_weight_fraction) / 1.e3

    def compute_partials(self, inputs, partials):
        lift_to_drag_ratio = inputs['lift_to_drag_ratio'].flatten()
        propellant_weight_fraction = inputs['propellant_weight_fraction'].flatten()
        cruise_speed = inputs['cruise_speed'].flatten()
        tsfc = inputs['tsfc'].flatten()
        
        partials['range_km', 'cruise_speed'] = -(1 / tsfc) * lift_to_drag_ratio * np.log(1 - propellant_weight_fraction) / 1.e3
        partials['range_km', 'tsfc'] = (cruise_speed / tsfc ** 2.) * lift_to_drag_ratio * np.log(1 - propellant_weight_fraction) / 1.e3
        partials['range_km', 'lift_to_drag_ratio'] = -((cruise_speed / tsfc) * np.log(1 - propellant_weight_fraction)) / 1.e3
        partials['range_km', 'propellant_weight_fraction'] = (cruise_speed / tsfc) * lift_to_drag_ratio / (1 - propellant_weight_fraction) / 1.e3


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
    comp.add_output('propellant_weight_fraction', 0.25 * np.random.random(shape))
    prob.model.add_subsystem('input_comp', comp, promotes=['*'])

    comp = BreguetRangeComp(
        shape=shape,
       
    )
    prob.model.add_subsystem('comp', comp, promotes=['*'])

    prob.setup(check=True)
    prob.run_model()
    prob.model.list_outputs()
    prob.check_partials(compact_print=True)

