from lsdo_utils.api import OptionsDictionary, float_types, units

# from lsdo_aircraft.aerodynamics.aerodynamics_group import AerodynamicsGroup


class LiftingSurface(OptionsDictionary):
    def initialize(self):
        self.declare('name', types=str)
        self.declare('area', default=1., types=float_types)
        self.declare('aspect_ratio', default=1., types=float_types)
        self.declare('taper_ratio', default=1., types=float_types)
        self.declare('sweep_deg', default=0., types=float_types)
        self.declare('CLmax', default=1.7, types=float_types)
        self.declare('CL0', default=0., types=float_types)
        self.declare('x_c_max_camber', default=0.25, types=float_types)
        self.declare('t_c', default=0.12, types=float_types)
        self.declare('mac', default=0.12, types=float_types)
        self.declare('mirror', default=True, types=bool)
        self.declare('cg_loc', default=0.35, types=float_types)
        self.declare('type_', default='wing', types=str)
        self.declare('multiplicative_factor', default=1., types=float_types)
        self.declare('additive_factor', default=0., types=float_types)
        self.declare('F', default=1.07 * (1 + 0.15)**2., types=float_types)
        self.declare('Q', default=1., types=float_types)
