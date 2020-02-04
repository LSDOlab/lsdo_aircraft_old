from openmdao.api import Problem, IndepVarComp

from lsdo_aircraft.api import Body, LiftingSurface, MiscellaneousPart, Rotor, WeightsGroup

n = 100
shape = (n, n)
'''
Change 'n' to change the shape of the inputs and outputs of your components. This is the same shape function
that was seen previously in run.py.
'''

aircraft = Body()
'''
Lines 21-28 specify the type of propulsion system that will be used for your aircraft.

    Preprocess and atmosphere are necessary for every type of aircraft !!
    Comment out the names that you will not need, make sure to also comment out any modules, and links that include that name.

    For example, if I were using a turboprop engine, then I would comment out:

            battery_name = 'battery'
            motor_name = 'motor'
            rotor_name = 'rotor'
            reciprocating_name = 'reciprocating'
            turbofan_name = 'turbofan'

    I would also comment out:

            powertrain.add_module(SimpleBattery(
            name=battery_name,
            ))
            powertrain.add_module(SimpleMotor(
                name=motor_name,
            ))
            powertrain.add_module(SimpleRotor(
                name=rotor_name,
            ))
            powertrain.add_module(SimpleReciprocating(
                name=reciprocating_name,
            ))
            powertrain.add_module(SimpleTurbofan(
                name=turbofan_name,
            ))

    As well as:

            powertrain.add_link(
                preprocess_name, 'time',
                battery_name, 'time',
            )
            powertrain.add_link(
                motor_name, ['angular_speed', 'shaft_power'],
                rotor_name, ['angular_speed', 'shaft_power'],
            )
            powertrain.add_link(
                preprocess_name, 'speed',
                rotor_name, 'speed',
            )
            powertrain.add_link(
                atmosphere_name, ['density', 'sonic_speed'],
                rotor_name, ['density', 'sonic_speed'],
            )
            powertrain.add_link(
                atmosphere_name, ['density'],
                reciprocating_name, ['density'],
            )
            powertrain.add_link(
                atmosphere_name, ['density', 'mach_number'],
                turbofan_name, ['density', 'mach_number'],
            )

Note:  If your aircraft uses a hybrid powertrain, you need to make the required links between different             modules.
'''

aircraft.add_part(
    LiftingSurface(name='Wing', mirror=True, reference=False, type_='wing'))

prob = Problem()
'''
Below you would define constants that are characteristic of your mission. If you want to change any of the other parameters of your mission, you can modify the independent variable components inside the relevant groups.
'''

group = WeightsGroup(shape=shape, aircraft=aircraft)
prob.model.add_subsystem('group', group, promotes=['*'])
'''
The line below would check if the connections are setup for all the components even before you run the model. If there are any components that are not connected, it would list them out before running the model.
'''
prob.setup(check=True)
'''
This runs the model and prints out all the outputs of your problem. If there were any connection issues listed out from the line above, you can see the values of the outputs for those.
'''
prob.run_model()
prob.model.list_outputs(print_arrays=True, prom_name=True)
