from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import LinearCombinationComp, PowerCombinationComp, constants

from lsdo_aircraft.sizing_gross_weight.gross_weight_comp import GrossWeightComp
from lsdo_aircraft.sizing_gross_weight.empty_weight_fraction_comp import EmptyWeightFractionComp
from lsdo_aircraft.sizing_gross_weight.breguet_propellant_weight_fraction_comp import BreguetPropellantWeightFractionComp


class SizingGrossWeightGroup(Group):

    """
        This Group is a container for all the components required in the computation of gross weight of the aircraft.  
    """

    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft')

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']

        a, c = aircraft.empty_weight_fraction_parameters
        k_vs = aircraft.empty_weight_fraction_k_vs
        weight_max = aircraft['empty_weight_fraction_weight_max']

        comp = IndepVarComp()
        comp.add_output('battery_energy_density', val=aircraft['battery_energy_density'], shape=shape)
        comp.add_output('propulsive_efficiency', val=aircraft['propulsive_efficiency'], shape=shape)
        comp.add_output('tsfc', val=aircraft['tsfc'], shape=shape)
        self.add_subsystem('inputs_comp', comp, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            powers_dict=dict(
                range_km=1.,
            ),
            out_name='range',
            coeff=1.e3,
        )
        self.add_subsystem('range_comp', comp, promotes=['*'])

        if aircraft['energy_source_type'] == 'electric':
            comp = PowerCombinationComp(
                shape=shape,
                powers_dict=dict(
                    range=1.,
                    battery_energy_density=-1.,
                    propulsive_efficiency=-1.,
                    lift_to_drag_ratio=-1.,
                ),
                out_name='propellant_weight_fraction',
                coeff=constants.g,
            )
            self.add_subsystem('propellant_weight_fraction_comp', comp, promotes=['*'])
        else:
            comp = BreguetPropellantWeightFractionComp(
                shape=shape,
            )
            self.add_subsystem('propellant_weight_fraction_comp', comp, promotes=['*'])

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