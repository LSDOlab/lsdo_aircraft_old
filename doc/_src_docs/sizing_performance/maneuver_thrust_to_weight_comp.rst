Maneuver thrust to weight comp
==============================

.. list-table:: List of options
  :header-rows: 1
  :widths: 15, 10, 20, 20, 30
  :stub-columns: 0

  *  -  Option
     -  Default
     -  Acceptable values
     -  Acceptable types
     -  Description
  *  -  distributed
     -  False
     -  [True, False]
     -  ['bool']
     -  True if the component has variables that are distributed across multiple processes.
  *  -  shape
     -  <object object at 0x8206719d0>
     -  None
     -  ['tuple']
     -  
  *  -  out_name
     -  <object object at 0x8206719d0>
     -  None
     -  ['str']
     -  
  *  -  in_names
     -  None
     -  None
     -  ['str', 'list']
     -  
  *  -  powers
     -  None
     -  None
     -  ['ndarray']
     -  
  *  -  terms_list
     -  None
     -  None
     -  ['list']
     -  
  *  -  constant
     -  0.0
     -  None
     -  ['int', 'float', 'ndarray']
     -  
  *  -  coeffs
     -  None
     -  None
     -  ['list', 'ndarray']
     -  

Class
-----

.. autoclass:: lsdo_aircraft.sizing_performance.maneuver_thrust_to_weight_comp.ClimbThrustToWeightComp

  .. automethod:: lsdo_aircraft.sizing_performance.maneuver_thrust_to_weight_comp.ClimbThrustToWeightComp.__init__