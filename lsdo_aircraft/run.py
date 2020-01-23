from openmdao.api import Problem, IndepVarComp

from lsdo_utils.api import units, constants

from lsdo_aircraft.aircraft import Aircraft

from lsdo_aircraft.sizing_gross_weight.sizing_gross_weight_group import SizingGrossWeightGroup
from lsdo_aircraft.sizing_performance.sizing_performance_group import SizingPerformanceGroup


shape = (2, 3)

energy_source_type = 'electric'
# energy_source_type = 'fuel_burning'

if energy_source_type == 'electric':
    payload_weight = 4 * 230 * units('N', 'lbf')
    crew_weight = 1 * 230 * units('N', 'lbf')
    range_km = 100.
    lift_to_drag_ratio = 10.
    cruise_speed = 67.
    thrust_source_type = 'propeller'
    landing_distance_ft = 8000.
    ref_wing_loading_lbf_ft2 = 25.
    ref_thrust_to_weight = 0.6
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

aircraft = Aircraft(
    aircraft_type='transport',
    empty_weight_fraction_variable_sweep=False,
    battery_energy_density_Wh_kg=150.,
    propulsive_efficiency=0.85,
    tsfc=1.e-4,
    energy_source_type=energy_source_type,
    thrust_source_type=thrust_source_type,
    stall_speed=cruise_speed * 0.6,
    climb_speed=cruise_speed * 0.8,
    turn_speed=cruise_speed * 0.8,
    landing_distance_ft=landing_distance_ft,
    ref_wing_loading_lbf_ft2=ref_wing_loading_lbf_ft2,
    ref_thrust_to_weight=ref_thrust_to_weight,
)

prob = Problem()

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
prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

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

prob.setup(check=True)
prob.run_model()

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