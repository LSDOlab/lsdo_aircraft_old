from openmdao.api import Problem, IndepVarComp

from lsdo_utils.api import units, constants

from lsdo_aircraft.aircraft import Aircraft

from lsdo_aircraft.sizing_gross_weight.sizing_gross_weight_group import SizingGrossWeightGroup

import numpy as np



# This defines the shape of all the parameters for the aircraft. By defining it as (1,), this means that you will be giving only one input for each aircraft variable. 
# It is important to note, that the variables can either be single values, or they have to be provided in the shape that is specified. 
# For example:
#             - If you want to run the program at 2 different payloads. You would define the shape as (2, ). Then when providing the input parameter value 
#               you would need to do this:
#                                            payload_weight = np.array([400, 500])    
#             
#             - Essentially, you can use this feature to try out many different combinations of input values, with only one run of the program. 
#               
#               A more complex example:
#                           - You want to evaluate your design at 3 different payloads and two different ranges. You would set the shape to a (2, 3) or (3, 2),
#                             and you would define the values of payload and range as so:
#                                   
#                                payload_weight = np.array([[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ],[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ]])
#                                range_km = np.array([[100., 100, 100] , [200, 200 , 200]])
#         
#                                The other variables you can just remain as a single value, because the program will automatically make them into a (2, 3) matrix.
#              
shape = (2, 3)



# Propulsion_type specifies whether you're using an electric or fuel-burning aircraft. Different equations apply
# based on which type you choose. 

propulsion_type = 'electric'
# propulsion_type = 'fuel_burning'


# Constants, and units are imported from lsdo_utils. Allows for the use of gravity, as well as converting between SI and Imperial units. 
lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

# Depending on whether the aircraft is fuel-burning or electric, you need to change the values under the corresponding 'if' statement. 
if propulsion_type == 'electric':
    payload_weight = np.array([[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ],[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ]])  
    crew_weight = 1 * 230 * N_lb
    range_km = np.array([[100., 100, 100] , [200, 200 , 200]])
    lift_to_drag_ratio = 10.
    cruise_speed = 67.
elif propulsion_type == 'fuel_burning':
    payload_weight = 400 * 230 * N_lb
    crew_weight = 10 * 230 * N_lb
    range_km = 6500.
    lift_to_drag_ratio = 15.
    cruise_speed = 230.

# These are properties of the aircraft which do not vary during the optimization. They are stored in a dictionary (a method of storing information in python). 
aircraft = Aircraft(
    empty_weight_fraction_ac_type='transport',  # Depending on the aircraft (ac) type, you will have a different value for empty weight fraction. 
                                                # Available options for empty_weight_fraction_ac_type are: 'transport' , 'ga_single' , and 'ga_twin'

    empty_weight_fraction_variable_sweep=False, # If you have decided that your aircraft wing has variable sweep, then set this to True. 

    battery_energy_density_Wh_kg=150.,  
    propulsive_efficiency=0.85,
    tsfc=1.e-4,                                 # Thrust Specific Fuel Consumption
    propulsion_type=propulsion_type,            # Do not change this, this is assigning the value that you have chosen earlier, whether the aircraft is electric or fuel-burning 
)

prob = Problem()

comp = IndepVarComp()
comp.add_output('payload_weight', val=payload_weight, shape=shape)              # Do not change this, this is assigning the value that you have chosen earlier for the electric or fuel-burning aircraft
comp.add_output('crew_weight', val=crew_weight, shape=shape)                    # Do not change this, this is assigning the value that you have chosen earlier for the electric or fuel-burning aircraft
comp.add_output('range_km', val=range_km, shape=shape)                          # Do not change this, this is assigning the value that you have chosen earlier for the electric or fuel-burning aircraft
comp.add_output('lift_to_drag_ratio', val=lift_to_drag_ratio, shape=shape)      # Do not change this, this is assigning the value that you have chosen earlier for the electric or fuel-burning aircraft
comp.add_output('cruise_speed', val=cruise_speed, shape=shape)                  # Do not change this, this is assigning the value that you have chosen earlier for the electric or fuel-burning aircraft 

prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])                   # Adding the subsystem of Independent Variable Components to your model. 

# This will create a SizingGrossWeightGroup for your openmdao model.
group = SizingGrossWeightGroup(
    shape=shape,
    aircraft=aircraft,
)
prob.model.add_subsystem('group', group, promotes=['*'])        # This adds your group to your model.

prob.setup(check=True)                                          # This sets up the problem.
prob.run_model()                                                # This runs the model.

print(sum([
    prob[name]
    for name in [
        'payload_weight',
        'crew_weight',
        'empty_weight',
        'propellant_weight',
    ]
]))
for name in [
    'payload_weight',
    'crew_weight',
    'empty_weight',
    'propellant_weight',
    'gross_weight',
    'empty_weight_fraction',
    'propellant_weight_fraction',
    'range',
    'lift_to_drag_ratio',
    'propulsive_efficiency',
    'battery_energy_density',
]:
    print(name, prob[name][0, 0])