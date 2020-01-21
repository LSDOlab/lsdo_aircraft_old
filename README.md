Installation instructions
=========================

1. Install `openmdao` by entering into terminal (from any directory):

  `pip install openmdao`

2. Install `sphinx_auto_embed` (a package used in creating the documentation used here) by entering into terminal (from any directory):

  `pip install git+https://github.com/hwangjt/sphinx_auto_embed.git`

3. Go to a directory where you want to install all your packages, and enter into terminal:

  `git clone https://github.com/lsdolab/lsdo_utils`

4. Go into the cloned `lsdo_utils` directory (by typing `cd lsdo_utils`) and type:

  `pip install -e .`

5. Go to a directory where you want to install all your packages, and enter into terminal:

  ` git clone https://github.com/lsdolab/lsdo_aircraft`

6. Go into the cloned `lsdo_aircraft` directory (by typing `cd lsdo_aircraft`) and type:

  `pip install -e .`

7. Build documentation by going into `lsdo_aircraft/doc` and type:

  `sphinx_auto_embed`

  `make html`

8. You can view the docs by opening `lsdo_aircraft/doc/_build/html/index.html`.