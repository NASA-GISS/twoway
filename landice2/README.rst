This program creates a ``GIC`` (Ground Initial Condition) and ``TOPO``
input files that use elevation classes over the Greenland Ice Sheet.
These input files are used by the rundeck ``E4F40EC.py``, which is a
variant of the traditional ``E4F40.R``.

The ``GIC`` and ``TOPO`` files are created based on pre-existing input
files, found according to the environment variable
``MODELE_FILE_PATH``.  To run this program:

1. Install the IceBin coupling library and software stack, according
   to the instructions:
   https://github.com/citibeth/icebin/blob/develop/README.rst

2. Type ``make``

The resulting files will be called ``Z2HX2fromZ1QX1N_EC.nc`` and
``GIC.144X90.DEC01.1.ext_1_EC.nc``, and will be placed in the current
directory.  From there, they may be placed in suitable locations for
ModelE input files.

- **To change the input files** (i.e. add elevation classes to other
  input files): Edit top of add_fhc.py

- **To change the elevation class definitions:** edit
  ``write_icebin_in_base.py`` (see ``hpdefs``).

- **To plot/regrid ModelE results from the elevation classes:** use
  the Python3 ``icebin`` package, along with the file
  ``icebin_in.nc``.

- Elevation classes are currently computed based on 20km ice grid
  cells.  To compute them based on a finer grid, one would have to
  replace ``elev_mask.cdl`` with equivalent data from some other
  hi-resolution DEM (digital elevation model) of the Greenland Ice
  Sheet.  The current DEM was taken from PISM.
