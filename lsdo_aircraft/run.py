from openmdao.api import Problem, IndepVarComp

from lsdo_utils.api import units, constants

from lsdo_aircraft.aircraft import Aircraft

from lsdo_aircraft.sizing_gross_weight.sizing_gross_weight_group import SizingGrossWeightGroup


shape = (2, 3)

propulsion_type = 'electric'
# propulsion_type = 'fuel_burning'

lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

if propulsion_type == 'electric':
    payload_weight = 4 * 230 * N_lb
    crew_weight = 1 * 230 * N_lb
    range_km = 100.
    lift_to_drag_ratio = 10.
    cruise_speed = 67.
elif propulsion_type == 'fuel_burning':
    payload_weight = 400 * 230 * N_lb
    crew_weight = 10 * 230 * N_lb
    range_km = 6500.
    lift_to_drag_ratio = 15.
    cruise_speed = 230.

aircraft = Aircraft(
    empty_weight_fraction_ac_type='transport',
    empty_weight_fraction_variable_sweep=False,
    battery_energy_density_Wh_kg=150.,
    propulsive_efficiency=0.85,
    tsfc=1.e-4,
    propulsion_type=propulsion_type,
)

prob = Problem()

comp = IndepVarComp()
comp.add_output('payload_weight', val=payload_weight, shape=shape)
comp.add_output('crew_weight', val=crew_weight, shape=shape)
comp.add_output('range_km', val=range_km, shape=shape)
comp.add_output('lift_to_drag_ratio', val=lift_to_drag_ratio, shape=shape)
comp.add_output('cruise_speed', val=cruise_speed, shape=shape)
prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

group = SizingGrossWeightGroup(
    shape=shape,
    aircraft=aircraft,
)
prob.model.add_subsystem('group', group, promotes=['*'])

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