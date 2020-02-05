from lsdo_utils.api import OptionsDictionary, float_types, units


class NonliftingSurface(OptionsDictionary):
    def initialize(self):
        self.declare('name', types=str)
        self.declare('u')
        self.declare('v')
        self.declare('offset', default={'x': 0, 'y': 0, 'z': 0}, types=dict)
        self.declare('weight', default=0., types=float_types)
        self.declare('weight_kg', default=None)
        self.declare('weight_lb', default=None)
        self.declare('CDp', default=0., types=float_types)
        self.declare('ref_area', default=1., types=float_types)
        self.declare('mirror', default=True, types=bool)
        if self['weight_kg'] is not None:
            self['weight'] = self['weight_kg'] * 9.81
        if self['weight_lb'] is not None:
            self['weight'] = self['weight_lb'] / 2.2 * 9.81
