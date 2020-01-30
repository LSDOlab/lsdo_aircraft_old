
from openmdao.api import Group, IndepVarComp
import numpy as np
from lsdo_utils.comps.arithmetic_comps.power_combination_comp import PowerCombinationComp
from lsdo_utils.comps.arithmetic_comps.linear_combination_comp import LinearCombinationComp


class MotorGroup(Group):
    def initialize(self):
        """
            The following variables are the ones that the user needs to modify:

                P - motor power
                omega - motor speed (shaft speed)

            These are the variables being computed:

                L - length of the motor
                r2 - inner diameter of the motor
                r1 - shaft radius

            The following variables are to be left as constant. The values should not be modified:
                r4 - outer diameter of the motor
                t_max - maximum operating temperature
                rho_cu - copper density
                rho_fe - iron density
                rho_md - magnet density
                rho_resistivity - resistivity of copper
                b_mg - peak gap magnetic flux density (initial value: 0.9 [T])
                a_m - line current density (initial value: 8.5*10^4 [A/m])
                eta_so - stator overhead mass (initial value: 1.5 [kg])
                eta_ro - rotor overhead mass (initial value: 1.2 [kg])
                kw1 - winding factor (initial value: 0.933)
                tau_ti - the yield stress for the titanium shaft

        """
        self.options.declare('shape', types=tuple)

        self.options.declare('r4', types=np.ndarray)
        self.options.declare('P', types=np.ndarray)
        self.options.declare('omega', types=np.ndarray)
        self.options.declare('t_env', types=np.ndarray)

        self.options.declare('tau_ti', types=np.ndarray)
        self.options.declare('t_max', types=np.ndarray)
        self.options.declare('rho_cu', types=np.ndarray)
        self.options.declare('rho_fe', types=np.ndarray)
        self.options.declare('rho_md', types=np.ndarray)
        self.options.declare('rho_ti', types=np.ndarray)
        self.options.declare('rho_resistivity', types=np.ndarray)
        self.options.declare('b_mg', types=np.ndarray)
        self.options.declare('a_m', types=np.ndarray)
        self.options.declare('eta_so', types=np.ndarray)
        self.options.declare('eta_ro', types=np.ndarray)
        self.options.declare('kw1', types=np.ndarray)
        self.options.declare('k_cu', types=np.ndarray)

    def setup(self):
        shape = self.options['shape']

        IVC = IndepVarComp()
        IVC.add_output('hysterisis_coeff', val=3*10**-3)
        IVC.add_output('frequency', val=400, shape=shape)
        IVC.add_output('P', val=60000, shape=shape)
        IVC.add_output('rpm', val=7000, shape=shape)
        IVC.add_output('r4', val=0.094, shape=shape)
        IVC.add_output('t_env', val=293, shape=shape)
        IVC.add_output('tau_ti', val=550 * 10 ** 6, shape=shape)
        IVC.add_output('t_max_ref', val=433, shape=shape)
        IVC.add_output('rho_ti', val=4506, shape=shape)
        IVC.add_output('rho_cu', val=8960, shape=shape)
        IVC.add_output('rho_fe', val=7874, shape=shape)
        IVC.add_output('rho_md', val=7010, shape=shape)
        IVC.add_output('rho_resistivity', val=1.68 * 10 ** -8, shape=shape)
        IVC.add_output('b_mg', val=0.9, shape=shape)
        IVC.add_output('a_m', val=8.5 * 10 ** 4, shape=shape)
        IVC.add_output('eta_so', val=1.5, shape=shape)
        IVC.add_output('eta_ro', val=1.2, shape=shape)
        IVC.add_output('eta_slot', val=0.5, shape=shape)
        IVC.add_output('eta_fill', val=0.5, shape=shape)
        IVC.add_output('kw1', val=0.933, shape=shape)
        IVC.add_output('k_cu', val=386, shape=shape)
        self.add_subsystem('IVC', IVC, promotes=['*'])

        # r4 = self.options['r4']
        # # P = self.options['P']
        # # omega = self.options['omega']
        # t_env = self.options['t_env']
        #
        # tau_ti = self.options['tau_ti']
        # t_max = self.options['t_max']
        # rho_cu = self.options['rho_cu']
        # rho_fe = self.options['rho_fe']
        # rho_md = self.options['rho_md']
        # rho_resistivity = self.options['rho_resistivity']
        # b_mg = self.options['b_mg']
        # a_m = self.options['a_m']
        # eta_so = self.options['eta_so']
        # eta_ro = self.options['eta_ro']
        # kw1 = self.options['kw1']
        # k_cu = self.options['k_cu']

        omega = PowerCombinationComp(
            shape=shape,
            in_names=['rpm'],
            out_name='omega',
            powers=[1.],
            coeff=(2*np.pi/60),
        )

        self.add_subsystem('omega_comp', omega, promotes=['*'])

        num_poles = PowerCombinationComp(
            shape=shape,
            in_names=['frequency', 'rpm'],
            out_name='num_poles',
            powers=[1., -1.],
            coeff=(120),
        )

        self.add_subsystem('num_poles_comp', num_poles, promotes=['*'])

        torque = PowerCombinationComp(
            shape=shape,
            in_names=['P', 'omega'],
            out_name='torque',
            powers=[1., -1.],
            coeff=1.,
        )

        self.add_subsystem('torque', torque, promotes=['*'])

        shaft_radius = PowerCombinationComp(
            shape=shape,
            in_names=['torque', 'tau_ti'],
            out_name='shaft_radius',
            powers=[1 / 3, -1 / 3],
            coeff=((5 * 2) / np.pi) ** (1 / 3),
        )

        self.add_subsystem('shaft_radius', shaft_radius, promotes=['*'])

        airgap_radius = PowerCombinationComp(
            shape=shape,
            in_names=['r4'],
            out_name='airgap_radius',
            powers=[1.],
            coeff=1./3.,
        )

        self.add_subsystem('airgap_radius', airgap_radius, promotes=['*'])

        stator_thickness = LinearCombinationComp(
            shape=shape,
            in_names=['r4', 'airgap_radius'],
            out_name='stator_thickness',
            coeffs=[1., -1.],
            constant=0.0,
        )

        self.add_subsystem('stator_thickness', stator_thickness, promotes=['*'])

        motor_length = PowerCombinationComp(
            shape=shape,
            in_names=['r4'],
            out_name='motor_length',
            powers=[1.],
            coeff= 1.2,
        )

        self.add_subsystem('motor_length', motor_length, promotes=['*'])

        t_increase = PowerCombinationComp(
            shape=shape,
            in_names=['rho_resistivity', 'eta_slot', 'eta_fill', 'k_cu', 'a_m'],
            out_name='t_increase',
            powers=[1., -1., -1., -1., 2.],
            coeff=0.5,
        )

        self.add_subsystem('t_increase', t_increase, promotes=['*'])

        t_max = LinearCombinationComp(
            shape=shape,
            in_names=['t_env', 't_increase'],
            out_name='t_max',
            coeffs=[1., 1.],
            constant=0.0,
        )

        self.add_subsystem('t_max', t_max, promotes=['*'])

        stator_mass_temp_1 = PowerCombinationComp(
            shape=shape,
            in_names=['rho_cu', 'eta_slot', 'eta_fill'],
            out_name='stator_temp_1',
            powers=[1., 1., 1.],
            coeff=1.0,
        )
        self.add_subsystem('stator_temp_1', stator_mass_temp_1, promotes=['*'])

        stator_mass_temp_2 = PowerCombinationComp(
            shape=shape,
            in_names=['rho_fe', 'eta_slot'],
            out_name='stator_temp_2',
            powers=[1., 1.],
            coeff=1.0,
        )
        self.add_subsystem('stator_temp_2', stator_mass_temp_2, promotes=['*'])

        stator_mass_temp_3 = LinearCombinationComp(
            shape=shape,
            in_names=['stator_temp_1', 'stator_temp_2', 'rho_fe'],
            out_name='stator_temp_3',
            coeffs=[1., -1., 1.],
            constant=0.0,
        )
        self.add_subsystem('stator_temp_3', stator_mass_temp_3, promotes=['*'])

        stator_mass_temp_4 = LinearCombinationComp(
            shape=shape,
            in_names=['airgap_radius', 'r4'],
            out_name='stator_temp_4',
            coeffs=[1., 1.],
            constant=0.0,
        )
        self.add_subsystem('stator_temp_4', stator_mass_temp_4, promotes=['*'])

        stator_mass = PowerCombinationComp(
            shape=shape,
            in_names=['eta_so', 'stator_thickness', 'motor_length', 'stator_temp_3', 'stator_temp_4'],
            out_name='stator_mass',
            powers=[1.0, 1.0, 1.0, 1.0, 1.0],
            coeff=np.pi
        )
        self.add_subsystem('stator_mass', stator_mass, promotes=['*'])

        rotor_mass_temp_1 = LinearCombinationComp(
            shape=shape,
            in_names=['airgap_radius', 'shaft_radius'],
            out_name='rotor_mass_temp_1',
            coeffs=[1., -1.],
            constant=0.0,
        )
        self.add_subsystem('rotor_mass_temp_1', rotor_mass_temp_1, promotes=['*'])

        rotor_mass_temp_2 = LinearCombinationComp(
            shape=shape,
            in_names=['airgap_radius', 'shaft_radius'],
            out_name='rotor_mass_temp_2',
            coeffs=[1., 1.],
            constant=0.0,
        )
        self.add_subsystem('rotor_mass_temp_2', rotor_mass_temp_2, promotes=['*'])

        rotor_mass = PowerCombinationComp(
            shape=shape,
            in_names=['rotor_mass_temp_1', 'rotor_mass_temp_2', 'eta_ro', 'motor_length', 'rho_md'],
            out_name='rotor_mass',
            powers=[1., 1., 1., 1., 1.],
            coeff=np.pi,
        )
        self.add_subsystem('rotor_mass', rotor_mass, promotes=['*'])

        shaft_mass = PowerCombinationComp(
            shape=shape,
            in_names=['shaft_radius', 'motor_length', 'rho_ti'],
            out_name='shaft_mass',
            powers=[2., 1., 1.],
            coeff=np.pi * 1.2
        )

        self.add_subsystem('shaft_mass_comp', shaft_mass, promotes=['*'])

        total_mass = LinearCombinationComp(
            shape=shape,
            in_names=['rotor_mass', 'stator_mass', 'shaft_mass'],
            out_name='total_mass',
            coeffs=[1., 1., 1.],
            constant=0.0,
        )
        self.add_subsystem('total_mass', total_mass, promotes=['*'])

        ohmic_loss = PowerCombinationComp(
            shape=shape,
            in_names=['airgap_radius', 'motor_length', 'rho_resistivity', 'a_m', 'eta_slot', 'eta_fill', 'stator_thickness'],
            out_name='ohmic_loss',
            powers=[1., 1., 1., 2., -1., -1., -1.],
            coeff=np.pi
        )

        self.add_subsystem('ohmic_loss_comp', ohmic_loss, promotes=['*'])

        # iron_loss_f = PowerCombinationComp(
        #     shape=shape,
        #     in_names=['omega'],
        #     out_name='f',
        #     powers=[1.],
        #     coeff=(60/(2*np.pi))
        #
        # )
        # self.add_subsystem('iron_loss_f_comp', iron_loss_f, promotes=['*'])

        eddy_loss = PowerCombinationComp(
            shape=shape,
            in_names=['b_mg', 'stator_mass', 'frequency'],
            out_name='eddy_loss',
            powers=[2., 1., 1.5],
            coeff=1.1 * (1 / 50) ** 1.5
        )

        self.add_subsystem('eddy_loss_comp', eddy_loss, promotes=['*'])

        hysterisis_loss = PowerCombinationComp(
            shape=shape,
            in_names=['b_mg', 'rotor_mass', 'frequency', 'hysterisis_coeff'],
            out_name='hysterisis_loss',
            powers=[2., 1., 1., 1.],
            coeff=1.0
        )

        self.add_subsystem('hysterisis_loss_comp', hysterisis_loss, promotes=['*'])

        iron_loss = LinearCombinationComp(
            shape=shape,
            in_names=['eddy_loss', 'hysterisis_loss'],
            out_name='iron_loss',
            coeffs=[1., 1],
            constant=0.0
        )

        self.add_subsystem('iron_loss_comp', iron_loss, promotes=['*'])



        power_input = LinearCombinationComp(
            shape=shape,
            in_names=['ohmic_loss', 'P', 'iron_loss'],
            out_name='power_input',
            coeffs=[1., 1.00, 1.],
            constant=0.
        )

        self.add_subsystem('power_input_comp', power_input, promotes=['*'])


        efficiency = PowerCombinationComp(

            shape=shape,
            in_names=['P', 'power_input'],
            out_name='efficiency',
            powers=[1., -1.],
            coeff=100
        )

        self.add_subsystem('efficiency_comp', efficiency, promotes=['*'])

        torque_available = PowerCombinationComp(
            shape=shape,
            in_names=['airgap_radius', 'motor_length', 'a_m', 'b_mg', 'kw1'],
            out_name='torque_available',
            powers=[1., 1., 1., 1., 1.],
            coeff=0.5
        )
        self.add_subsystem('torque_available_comp', torque_available, promotes=['*'])