from __future__ import print_function
import numpy as np
from openmdao.api import Group, IndepVarComp

from lsdo_utils.api import PowerCombinationComp

from lsdo_aircraft.atmosphere.temperature_comp import TemperatureComp
from lsdo_aircraft.atmosphere.pressure_comp import PressureComp
from lsdo_aircraft.atmosphere.density_comp import DensityComp
from lsdo_aircraft.atmosphere.sonic_speed_comp import SonicSpeedComp
from lsdo_aircraft.atmosphere.viscosity_comp import ViscosityComp
from lsdo_aircraft.aerodynamics.dynamic_pressure_comp import DynamicPressureComp
from lsdo_utils.comps.arithmetic_comps.ks_comp import \
    KSComp
from lsdo_utils.comps.array_comps.array_reshape_comp import \
    ArrayReshapeComp
from lsdo_utils.comps.array_comps.scalar_expansion_comp import \
    ScalarExpansionComp


class AtmosphereGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('module')

        self.promotes = None

    def setup(self):
        shape = self.options['shape']

        size = int(np.prod(shape))

        group = Group()

        comp = DynamicPressureComp(
            shape=shape,
            rho_name='density',
            v_name='speed',
            dynamic_pressure_name='dynamic_pressure',
        )
        group.add_subsystem('dynamic_pressure_comp', comp, promotes=['*'])

        comp = ArrayReshapeComp(
            in_name='dynamic_pressure',
            out_name='dynamic_pressure_tmp',
            in_shape=shape,
            out_shape=(1, size),
        )
        group.add_subsystem('dynamic_pressure_reshape_comp',
                            comp,
                            promotes=['*'])

        comp = KSComp(
            in_name='dynamic_pressure_tmp',
            out_name='max_dynamic_pressure_scalar',
            shape=(1, ),
            constraint_size=size,
            lower_flag=False,
            rho=100.,
            bound=0.,
        )
        group.add_subsystem('max_dynamic_pressure_scalar_comp',
                            comp,
                            promotes=['*'])

        comp = ScalarExpansionComp(
            shape=shape,
            in_name='max_dynamic_pressure_scalar',
            out_name='max_dynamic_pressure',
        )
        group.add_subsystem('max_dynamic_pressure_comp', comp, promotes=['*'])
        self.add_subsystem('dynamic_pressure', group, promotes=['*'])

        comp = PowerCombinationComp(
            shape=shape,
            out_name='altitude_km',
            coeff=1.e-3,
            powers_dict=dict(altitude=1., ),
        )
        self.add_subsystem('altitude_km_comp', comp, promotes=['*'])

        comp = TemperatureComp(shape=shape)
        self.add_subsystem('temperature_comp', comp, promotes=['*'])

        comp = PressureComp(shape=shape)
        self.add_subsystem('pressure_comp', comp, promotes=['*'])

        comp = DensityComp(shape=shape)
        self.add_subsystem('density_comp', comp, promotes=['*'])

        comp = SonicSpeedComp(shape=shape)
        self.add_subsystem('sonic_speed_comp', comp, promotes=['*'])

        comp = ViscosityComp(shape=shape)
        self.add_subsystem('viscosity_comp', comp, promotes=['*'])

        # comp = PowerCombinationComp(
        #     shape=shape,
        #     out_name='mach_number',
        #     powers_dict=dict(
        #         speed=1.,
        #         sonic_speed=-1.,
        #     ),
        # )
        # self.add_subsystem('mach_number_comp', comp, promotes=['*'])
