from openmdao.api import Group

from lsdo_utils.api import LinearCombinationComp, PowerCombinationComp

from lsdo_tada.sizing_gross_weight.gross_weight_comp import GrossWeightComp
from lsdo_tada.sizing_gross_weight.empty_weight_fraction_comp import EmptyWeightFractionComp


class SizingGrossWeightGroup(Group):

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft')

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']

        a, c = aircraft.empty_weight_fraction_parameters
        k_vs = aircraft.empty_weight_fraction_k_vs
        weight_max = aircraft['empty_weight_fraction_weight_max']

        comp = LinearCombinationComp(
            shape=shape,
            in_names=['payload_weight', 'crew_weight'],
            out_name='fixed_weight',
        )
        self.add_subsystem('fixed_weight_comp', comp, promotes=['*'])

        comp = GrossWeightComp(
            shape=shape,
            a=a,
            c=c,
            k_vs=k_vs,
            weight_max=weight_max,
        )
        self.add_subsystem('gross_weight_comp', comp, promotes=['*'])

        comp = EmptyWeightFractionComp(
            shape=shape,
            a=a,
            c=c,
            k_vs=k_vs,
        )
        self.add_subsystem('empty_weight_fraction_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            in_names=['empty_weight_fraction', 'gross_weight'],
            out_name='empty_weight',
        )
        self.add_subsystem('empty_weight_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            in_names=['propellant_weight_fraction', 'gross_weight'],
            out_name='propellant_weight',
        )
        self.add_subsystem('propellant_weight_comp', comp, promotes=['*'])