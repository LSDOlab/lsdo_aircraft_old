from openmdao.api import Problem, IndepVarComp

from lsdo_utils.api import units, constants

from lsdo_tada.aircraft import Aircraft

from lsdo_tada.sizing_gross_weight.sizing_gross_weight_group import SizingGrossWeightGroup


shape = (2, 3)

lb_N = units('lb', 'kg') / constants.g
N_lb = 1. / lb_N

aircraft = Aircraft(
    empty_weight_fraction_ac_type='transport',
    empty_weight_fraction_variable_sweep=False,
)

prob = Problem()

comp = IndepVarComp()
comp.add_output('payload_weight', val=800 * N_lb, shape=shape)
comp.add_output('crew_weight', val=200 * N_lb, shape=shape)
comp.add_output('propellant_weight_fraction', val=0.25, shape=shape)
prob.model.add_subsystem('inputs_comp', comp, promotes=['*'])

group = SizingGrossWeightGroup(
    shape=shape,
    aircraft=aircraft,
)
prob.model.add_subsystem('group', group, promotes=['*'])

prob.setup()
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
    'gross_weight'
]:
    print(name, prob[name])