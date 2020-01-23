Empty weight fraction comp
==========================

.. list-table:: List of options
  :header-rows: 1
  :widths: 15, 10, 20, 20, 30
  :stub-columns: 0

  *  -  Option
     -  Default
     -  Acceptable values
     -  Acceptable types
     -  Description
  *  -  assembled_jac_type
     -  csc
     -  ['csc', 'dense']
     -  None
     -  Linear solver(s) in this group, if using an assembled jacobian, will use this type.
  *  -  distributed
     -  False
     -  None
     -  None
     -  True if the component has variables that are distributed across multiple processes.
  *  -  shape
     -  <object object at 0x1192d7ee0>
     -  None
     -  ['tuple']
     -  
  *  -  a
     -  <object object at 0x1192d7ee0>
     -  None
     -  ['float']
     -  
  *  -  c
     -  <object object at 0x1192d7ee0>
     -  None
     -  ['float']
     -  
  *  -  k_vs
     -  <object object at 0x1192d7ee0>
     -  None
     -  ['float']
     -  

Class
-----

.. autoclass:: lsdo_aircraft.sizing_gross_weight.empty_weight_fraction_comp.EmptyWeightFractionComp

  .. automethod:: lsdo_aircraft.sizing_gross_weight.empty_weight_fraction_comp.EmptyWeightFractionComp.__init__