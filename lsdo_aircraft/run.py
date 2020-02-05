from openmdao.api import Problem, IndepVarComp, ScipyOptimizeDriver

from lsdo_utils.api import units, constants

from lsdo_aircraft.aircraft import Aircraft

from lsdo_aircraft.sizing_gross_weight.sizing_gross_weight_group import SizingGrossWeightGroup
from lsdo_aircraft.sizing_performance.sizing_performance_group import SizingPerformanceGroup

import numpy as np

try:
    from lsdo_viz.api import Problem
except:
    pass

# This defines the shape of all the parameters for the aircraft. By defining it as (1,), this means that you will be giving only one input for each aircraft variable.
# It is important to note, that the variables can either be single values, or they have to be provided in the shape that is specified.
# For example:
# - If you want to run the program at 2 different payloads, you would define the shape as (2, ).
#   Then when providing the input parameter value you would need to do this:
#      payload_weight = np.array([400, 500])
# - Essentially, you can use this feature to try out many different combinations of input values, with only one run of the program.
# A more complex example:
# - You want to evaluate your design at 3 different payloads and two different ranges.
#   You would set the shape to a (2, 3), and you would define the values of payload and range as so:
#      payload_weight = np.array([[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ],[4 * 230 * N_lb, 5 * 230 * N_lb, 6 * 230 * N_lb ]])
#      range_km = np.array([[100., 100, 100] , [200, 200 , 200]])
#   The other variables you can just remain as a single value, because the program will automatically make them into a (2, 3) matrix.
num_sweep_points = 100
shape = (1 + num_sweep_points, )

# energy_source_type specifies whether you're using an electric or fuel-burning aircraft. Different equations apply
# based on which type you choose.

# energy_source_type = 'electric'
energy_source_type = 'fuel_burning'

# Constants, and units are imported from lsdo_utils. Allows for the use of gravity, as well as converting between SI and Imperial units.
lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

# Depending on whether the aircraft is fuel-burning or electric, you need to change the values under the corresponding 'if' statement.
if energy_source_type == 'electric':
    payload_weight = 4 * 230 * units('N', 'lbf')
    crew_weight = 1 * 230 * units('N', 'lbf')
    range_km = 100.
    lift_to_drag_ratio = 10.
    cruise_speed = 67.
    thrust_source_type = 'propeller'
    landing_distance_ft = 8000.
    ref_wing_loading_lbf_ft2 = 25.
    ref_thrust_to_weight = 0.3
    aircraft_type = 'ga_twin'
elif energy_source_type == 'fuel_burning':
    payload_weight = 400 * 230 * units('N', 'lbf')
    crew_weight = 10 * 230 * units('N', 'lbf')
    range_km = 6500.
    lift_to_drag_ratio = 15.
    cruise_speed = 230.
    thrust_source_type = 'jet'
    landing_distance_ft = 8000.
    ref_wing_loading_lbf_ft2 = 130.
    ref_thrust_to_weight = 0.3
    aircraft_type = 'transport'

wing_loading_lbf_ft2 = np.concatenate((
    ref_wing_loading_lbf_ft2 * np.ones(1),
    np.linspace(0.05 * ref_wing_loading_lbf_ft2, 2 * ref_wing_loading_lbf_ft2,
                num_sweep_points),
))
thrust_to_weight = np.concatenate((
    ref_thrust_to_weight * np.ones(1),
    np.linspace(0.05 * ref_thrust_to_weight, 2 * ref_thrust_to_weight,
                num_sweep_points),
))

# These are properties of the aircraft which do not vary during the optimization. They are stored in a dictionary (a method of storing information in python).
aircraft = Aircraft(
    aircraft_type=
    aircraft_type,  # Depending on the aircraft (ac) type, you will have a different value for empty weight 
    empty_weight_fraction_variable_sweep=
    False,  # If you have decided that your aircraft wing has variable sweep, then set this to True. 
    CL_max=1.5,
    CL_takeoff=1.5 / 1.21,
    battery_energy_density_Wh_kg=150.,
    propulsive_efficiency=0.85,
    tsfc=1.e-4,  # Thrust Specific Fuel Consumption
    energy_source_type=energy_source_type,
    thrust_source_type=thrust_source_type,
    stall_speed=cruise_speed * 0.6,
    climb_speed=cruise_speed * 0.8,
    turn_speed=cruise_speed * 0.8,
    landing_distance_ft=landing_distance_ft,
    wing_loading_lbf_ft2=wing_loading_lbf_ft2,
    thrust_to_weight=thrust_to_weight,
    ref_wing_loading_lbf_ft2=ref_wing_loading_lbf_ft2,
    ref_thrust_to_weight=ref_thrust_to_weight,
)

prob = Problem()
prob.aircraft = aircraft

comp = IndepVarComp()
comp.add_output('density', val=1.225, shape=shape)
comp.add_output('payload_weight', val=payload_weight, shape=shape)
comp.add_output('crew_weight', val=crew_weight, shape=shape)
comp.add_output('range_km', val=range_km, shape=shape)
comp.add_output('lift_to_drag_ratio', val=lift_to_drag_ratio, shape=shape)
comp.add_output('oswald_efficiency', val=0.8, shape=shape)
comp.add_output('aspect_ratio', val=8, shape=shape)
comp.add_output('cruise_speed', val=cruise_speed, shape=shape)
comp.add_output('CD0', val=0.0350, shape=shape)
prob.model.add_subsystem('inputs_comp', comp, promotes=[
    '*'
])  # Adding the subsystem of Independent Variable Components to your model.

# This will create a SizingGrossWeightGroup for your openmdao model.
group = SizingGrossWeightGroup(
    shape=shape,
    aircraft=aircraft,
)
prob.model.add_subsystem('sizing_gross_weight_group', group, promotes=['*'])

group = SizingPerformanceGroup(
    shape=shape,
    aircraft=aircraft,
)
prob.model.add_subsystem('sizing_performance_group', group, promotes=['*'])

prob.model.add_objective('sizing_performance_objective', index=0)

prob.driver = ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'
prob.driver.options['tol'] = 1e-15
prob.driver.options['disp'] = True

# This is to set up a different optimizer, SNOPT, which is faster but has a difficult set-up process
if 0:
    from openmdao.api import pyOptSparseDriver
    prob.driver = pyOptSparseDriver()
    prob.driver.options['optimizer'] = 'SNOPT'

prob.setup(check=True)
prob.run_model()
# prob.check_partials(compact_print=True)
prob.run_driver()
prob.model.list_outputs(prom_name=True)
print(prob['gross_weight'][1:])

# import matplotlib.pyplot as plt
# plt.plot(prob['wing_loading'][1:], prob['climb_power_to_weight'][1:])
# plt.show()
