from distutils.core import setup


setup(
    name='lsdo_tada',
    version='1',
    packages=[
        'lsdo_tada',
    ],
    install_requires=[
        'dash==1.2.0',
        'dash-daq==0.1.0',
    ],
)
