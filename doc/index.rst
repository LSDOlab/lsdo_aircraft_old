.. uam_mdo_v1 documentation master file, created by
   sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Large-scale system design optimization framework for aircraft design (lsdo_aircraft)
====================================================================================

This is a Python software library for aircraft conceptual design of aircraft.

The software design makes heavy use of object-oriented programming;
in other words, setting up a script for analysis or optimization involves instantiating a series of classes.
As is always the case in any OpenMDAO script, the OpenMDAO `Problem_` class is at the very top of the class hierarchy.

.. _Problem: http://openmdao.org/twodocs/versions/latest/basic_guide/first_optimization.html

Discipline models:

.. toctree::
   :maxdepth: 2
   :titlesonly:

   _src_docs/sizing_gross_weight/sizing_gross_weight


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
