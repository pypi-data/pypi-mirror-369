=====
pyTMD
=====

|License|
|Documentation Status|
|PyPI|
|conda-forge|
|commits-since|
|zenodo|

.. |License| image:: https://img.shields.io/github/license/pyTMD/pyTMD
   :target: https://github.com/pyTMD/pyTMD/blob/main/LICENSE

.. |Documentation Status| image:: https://readthedocs.org/projects/pytmd/badge/?version=latest
   :target: https://pytmd.readthedocs.io/en/latest/?badge=latest

.. |PyPI| image:: https://img.shields.io/pypi/v/pyTMD.svg
   :target: https://pypi.python.org/pypi/pyTMD/

.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/pytmd
   :target: https://anaconda.org/conda-forge/pytmd

.. |commits-since| image:: https://img.shields.io/github/commits-since/pyTMD/pyTMD/latest
   :target: https://github.com/pyTMD/pyTMD/releases/latest

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.5555395.svg
   :target: https://doi.org/10.5281/zenodo.5555395

Python-based tidal prediction software for estimating ocean, load, solid Earth and pole tides

For more information: see the documentation at `pytmd.readthedocs.io <https://pytmd.readthedocs.io/>`_

Installation
############

From PyPI:

.. code-block:: bash

   python3 -m pip install pyTMD

To include all optional dependencies:

.. code-block:: bash

   python3 -m pip install pyTMD[all]

Using ``conda`` or ``mamba`` from conda-forge:

.. code-block:: bash

   conda install -c conda-forge pytmd

.. code-block:: bash

   mamba install -c conda-forge pytmd

Development version from GitHub:

.. code-block:: bash

   python3 -m pip install git+https://github.com/pyTMD/pyTMD.git

Running with Pixi
-----------------

Alternatively, you can use `Pixi <https://pixi.sh/>`_ for a streamlined workspace environment:

1. Install Pixi following the `installation instructions <https://pixi.sh/latest/#installation>`_

2. Clone the project repository:

.. code-block:: bash

   git clone https://github.com/pyTMD/pyTMD.git

3. Move into the ``pyTMD`` directory

.. code-block:: bash

   cd pyTMD

4. Install dependencies and start JupyterLab:

.. code-block:: bash

   pixi run start

This will automatically create the environment, install all dependencies, and launch JupyterLab in the `notebooks <./doc/source/notebooks/>`_ directory.

Dependencies
############

- `dateutil: powerful extensions to datetime <https://dateutil.readthedocs.io/en/stable/>`_
- `lxml: processing XML and HTML in Python <https://pypi.python.org/pypi/lxml>`_
- `netCDF4: Python interface to the netCDF C library <https://unidata.github.io/netcdf4-python/>`_
- `numpy: Scientific Computing Tools For Python <https://www.numpy.org>`_
- `pyproj: Python interface to PROJ library <https://pypi.org/project/pyproj/>`_
- `scipy: Scientific Tools for Python <https://www.scipy.org/>`_
- `timescale: Python tools for time and astronomical calculations <https://pypi.org/project/timescale/>`_

References
##########

    T. C. Sutterley, T. Markus, T. A. Neumann, M. R. van den Broeke, J. M. van Wessem, and S. R. M. Ligtenberg,
    "Antarctic ice shelf thickness change from multimission lidar mapping", *The Cryosphere*,
    13, 1801-1817, (2019). `doi: 10.5194/tc-13-1801-2019 <https://doi.org/10.5194/tc-13-1801-2019>`_

    L. Padman, M. R. Siegfried, H. A. Fricker,
    "Ocean Tide Influences on the Antarctic and Greenland Ice Sheets", *Reviews of Geophysics*,
    56, 142-184, (2018). `doi: 10.1002/2016RG000546 <https://doi.org/10.1002/2016RG000546>`_

Download
########

| The program homepage is:
| https://github.com/pyTMD/pyTMD
| A zip archive of the latest version is available directly at:
| https://github.com/pyTMD/pyTMD/archive/main.zip

Alternative Software
####################

| perth5 from NASA Goddard Space Flight Center:
| https://codeberg.org/rray/perth5
| Matlab Tide Model Driver from Earth & Space Research:
| https://github.com/EarthAndSpaceResearch/TMD_Matlab_Toolbox_v2.5
| Fortran OSU Tidal Prediction Software:
| https://www.tpxo.net/otps

Disclaimer
##########

This package includes software developed at NASA Goddard Space Flight Center (GSFC) and the University of Washington Applied Physics Laboratory (UW-APL).
It is not sponsored or maintained by the Universities Space Research Association (USRA), AVISO or NASA.
The software is provided here for your convenience but *with no guarantees whatsoever*.
It should not be used for coastal navigation or any application that may risk life or property.

Contributing
############

This project contains work and contributions from the `scientific community <./CONTRIBUTORS.rst>`_.
If you would like to contribute to the project, please have a look at the `contribution guidelines <./doc/source/getting_started/Contributing.rst>`_, `open issues <https://github.com/pyTMD/pyTMD/issues>`_ and `discussions board <https://github.com/pyTMD/pyTMD/discussions>`_.

Credits
#######

The Tidal Model Driver (`TMD <https://github.com/EarthAndSpaceResearch/TMD_Matlab_Toolbox_v2.5>`_) Matlab Toolbox was developed by Laurie Padman, Lana Erofeeva and Susan Howard.
An updated version of the TMD Matlab Toolbox (`TMD3 <https://github.com/chadagreene/Tide-Model-Driver>`_) was developed by Chad Greene.
The OSU Tidal Inversion Software (OTIS) and OSU Tidal Prediction Software (`OTPS <https://www.tpxo.net/otps>`_) were developed by Lana Erofeeva and Gary Egbert (`copyright OSU <https://www.tpxo.net/tpxo-products-and-registration>`_, licensed for non-commercial use).
The NASA Goddard Space Flight Center (GSFC) PREdict Tidal Heights (PERTH3) software was developed by Richard Ray and Remko Scharroo.
An updated and more versatile version of the NASA GSFC tidal prediction software (`PERTH5 <https://codeberg.org/rray/perth5>`_) was developed by Richard Ray.

License
#######

The content of this project is licensed under the `Creative Commons Attribution 4.0 Attribution license <https://creativecommons.org/licenses/by/4.0/>`_ and the source code is licensed under the `MIT license <LICENSE>`_.
