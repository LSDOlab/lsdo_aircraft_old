from openmdao.api import Group, IndepVarComp
from lsdo_aircraft.api import (
    AerodynamicsGroup,
    DynamicPressureComp,
    ForceCoeffComp,
    ForceComp,
    LiftCoeffComp,
    LiftCurveSlopeComp,
    LiftingSurfaceFFComp,
    OswaldEfficiencyComp,
    ParasiticDragCoeffComp,
    ReynoldsComp,
    SkinFrictionCoeffComp,
    Body,
    LiftingSurface,
    NonliftingSurface,
    Rotor,
)


class GeometryGroup(Group):
    def initialize(self):
        self.options.declare('shape', types=tuple)
        self.options.declare('aircraft', types=Body)

    def setup(self):
        shape = self.options['shape']
        aircraft = self.options['aircraft']
        comp = IndepVarComp()
        for lifting_surface in aircraft['lifting_surfaces']:
            name = lifting_surface['name']
            cg = lifting_surface['cg']
            area = lifting_surface['area']
            aspect_ratio = lifting_surface['aspect_ratio']
            sweep_deg = lifting_surface['sweep_deg']
            taper_ratio = lifting_surface['taper_ratio']
            t_c = lifting_surface['t_c']
            comp.add_output('{}_area'.format(name), val=area, shape=shape)
            comp.add_output('{}_aspect_ratio'.format(name),
                            val=aspect_ratio,
                            shape=shape)
            comp.add_output('{}_sweep_deg'.format(name),
                            val=sweep_deg,
                            shape=shape)
            comp.add_output('{}_taper_ratio'.format(name),
                            val=taper_ratio,
                            shape=shape)
            comp.add_output('{}_t_c'.format(name), val=t_c, shape=shape)
        for nonlifting_surface in aircraft['nonlifting_surfaces']:
            name = nonlifting_surface['name']
            cg = nonlifting_surface['cg']
            area = nonlifting_surface['area']
            comp.add_output('{}_area'.format(name), val=area, shape=shape)
            comp.add_output('{}_cg'.format(name), val=cg, shape=shape)
        self.add_subsystem('indeps', comp, promotes=['*'])
