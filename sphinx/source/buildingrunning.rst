.. _modele-pism:

Building / Running ModelE-PISM Coupled Model
============================================

These instructions outline how to set up a coupled ModelE-PISM on
*discover* (or any computer), starting from scratch.  For the most
part, command lines that can be cut-n-pasted into *discover* are used;
but many pathes can be changed to suit your needs as well.

.. note::

   We assume the following paths throughout this tutorial.  The
   software may be installed in any place; and the user may set these
   paths however they like.  These environment variables do NOT need
   to be set to use this software, they are merely set for the
   purposes of this tutorial.

   .. code-block:: bash

      # Location of shared Spack instance containing installed
      # environment
      SPACK=~eafisch2/spack7

      # Location of user's Spack harness
      HARNESS=~/harness/twoway

      # Location of user's ModelE runs
      EXP=~/exp

      # Your username on the simplex git server
      SIMPLEX_USER=$USER

      # Where you will store downloaded ModelE input files
      # Use this location for discover; otherwise invent one
      INPUT_FILES=/discover/nobackup/projects/giss/prod_input_files


Build the Spack Environment
---------------------------

This builds the prerequisite software.  It only needs to be done once
by any user on the system; and shared by everyone else.

Clone Spack
```````````

Download the for of Spack containing tested recipes to build software
needed for ModelE-PISM coupling:

.. code-block:: bash

   cd $(dirname $SPACK)
   git clone git@github.com:citibeth/spack.git -b efischer/giss2 $(basename $SPACK))


Use Spack to Build Environement
```````````````````````````````

.. code-block:: bash

   $SPACK/bin/spack -e twoway-discover concretize -f
   $SPACK/bin/spack -e twoway-discover install
   $SPACK/bin/spack -e twoway-discover env loads -r
   cd $SPACK/var/spack/environments/twoway-discover
   sort loads | uniq >loads2
   cp loads2 loads

.. note::

   The *twoway-discover* Spack environment is meant to work on the
   *NCCS Discover* supercomputer.  If this is being built on another
   system, then *twoway-discover* should be copied, modified as
   appropriate for that system, checked in and submitted as a pull
   request.  Further details are out of the scope of this document;
   see `Spack Environments
   <https://spack.readthedocs.io/en/latest/environments.html`_:

   .. code-block:: bash

      cd $SPACK/var/spack/environments
      cp -r twoway-discover twoway-mything
      nano twoway-mything/spack.yaml


Make Sure Spack is World Readable
`````````````````````````````````

When you are done building the prerequisite software, it is polite to
make it world readable for everyone, so others can use it too:

.. code-block:: bash

   chmod -R go+r $SPACK


Set up your own Harness on the Spack Environment
------------------------------------------------

The Spack Environemnt above consists of all prerequisite packages,
plus a small number of packages you will build yourself.  A *Spack
Harness* consists of CMake setup scripts that use the Spack
Environment, but allow you to build your packages in your own private
location.  You can create as many harnesses as you like, for as many
checkouts / clones of the software as you like.

Start by creating *this* harness:

.. code-block:: bash

   $SPACK/bin/spack -e twoway-discover env harness -o $HARNESS

Load your Spack Environment
```````````````````````````

This needs to be done every time you log in or start a new shell.  You
might want to put it in your `.bashrc` file:

.. code-block:: bash

   source $HARNESS/loads-x


Clone Your Software
-------------------

Now clone the software you need:

.. code-block:: bash

   cd $HARNESS
   git clone git@github.com:citibeth/ibmisc.git
   git clone git@github.com:citibeth/icebin.git
   git clone git@github.com:citibeth/twoway.git
   git clone git@github.com:pism/pism.git -b efischer/dev


At this point you can clone ModelE.  You may wish to clone it multiple
times into multiple directories, based on different branches.

   git clone $SIMPLEX_USER@simplex.giss.nasa.gov:/giss/gitrepo/modelE.git -b e3/twoway
   cd modelE; ln -s ../modele-setup.py .; cd ..

.. note::

   Cloning ModelE requires you have an account on *simplex* at GISS.

Build the Software
------------------

It should be built in the order: *ibmisc*, *icebin*, *pism*.  The
first three are all built the same way:

.. code-block:: bash

   cd $HARNESS/ibmisc
   mkdir build
   cd build
   python3 ../../ibmisc-setup.py ..
   make install -j20

.. code-block:: bash

   cd $HARNESS/icebin
   mkdir build
   cd build
   python3 ../../icebin-setup.py ..
   make install -j20


.. code-block:: bash

   cd $HARNESS/pism
   mkdir build
   cd build
   python3 ../../pism-setup.py ..
   make install -j20

To clean a build:

.. code-block:: bash

   # rm -rf $HARNESS/ibmisc/build

In the future, if you edit any of these packages, you will need to
rebuild them.  If you edit header files in *ibmisc*, you will also
need to rebuild *icebin*.

Set up ModelE Input Files
-------------------------

ModelE uses two environment variables related to input files:

* ``MODELE_FILE_PATH``: A colon-separated list of directories where
  ModelE looks for input files.  Generally starts with ``.``, to allow
  ModelE to look in the run directory.


* ``MODELE_ORIGIN_DIR``: A single directory, to which missing input
  files will be downloaded.  Typically also contained in
  ``MODELE_FILE_PATH``.

These can be set up as follows:

.. code-block:: bash

   mkdir -p $INPUT_FILES

Add to *.bashrc*:

.. code-block:: bash

   # Where input files will be downloaded to if not found
   export MODELE_ORIGIN_DIR=$INPUT_FILES

   # Where to look for input files
   export MODELE_FILE_PATH=.:$INPUT_FILES

.. note::

   TODO: Rename these variables to be consistent with usage in
   ``.modelErc``, which uses ``GCMSEARCHPATH`` variable.


Set up your SLURM Configuration
-------------------------------

Add to *.bashrc*:

.. code-block:: bash

   export ECTL_LAUNCHER=slurm

.. note::

   TODO: Move this configuration parameter into the `ectl.conf` file.


Run ModelE Standalone
---------------------

Now you are ready to run ModelE, as explained in `modele-control docs
<https://modele-control.readthedocs.io/en/latest/>`_.  Start by
creating a top-level *experiment* directory, which will house a number of
*studies*:

.. code-block:: sh

   mkdir ~/exp
   echo >~/exp/ectl.conf   # Marks this as a project directory

Now you can create a *study directory*.  A study is a collection of
related ModelE *runs*:

.. code-block:: sh

   cd ~/exp
   mkdir mystudy

Now you can create a ModelE *run*.  This command configures a run based on:

1. A ModelE source location (`--src` flag).
2. A ModelE rundeck (`--rundeck` flag).
3. The directory in which the run should be created (positional argument).

.. code-block:: sh

   cd mystudy
   ectl setup --src ~/git/twoway-discover/modelE --rundeck ~/git/twoway-discover/modelE/templates/E6F40.R run1

Once the run directory has been created, the source and rundeck
locations don't need to be recreated.  You can just re-setup using one
of either:

.. code-block:: sh

   ectl setup run1
   cd run1; ectl setup .

Now you can run this:

.. code-block:: sh

   ectl run --help
   ectl run -ts 19491231,19500201

Now you can run it:

   ectl run -ts 19491231,19500102 -np 28 --time 11:00:00 --launcher slurm-debug run1

For more on running ModelE with ModelE-Control, see `ModelE-Control
Documentation <https://modele-control.readthedocs.io>`_.


Spinup PISM in Greenland
------------------------

These instuctions follow those in `PISM Docs <https://pism-docs.org/sphinx/manual/std-greenland/index.html>_`.

Create a spun-up PISM.  Normally, this would be part of the project
directory, and be used by multiple runs.

.. code-block:: bash

   # cd ~/exp/mystudy
   cp -r ~/git/pism/examples/std-greenland .
   cd std-greenland
   ./preprocess.sh nproc=12   # nproc = number of corse on your machine
   nice ./spinup.sh $nproc const 1000 20 sia g20km_10ka.nc


EC-Enabled TOPO File
--------------------

This step generates boundary condition (TOPO) files for use with
ModelE. There are two levels: uncoupled TOPO files may be used diretly
by ModelE for uncoupled runs, whereas copuled TOPO files are used for
coupled runs.  You may choose to generate either or both.

Uncoupled TOPO Files
````````````````````

The following generates TOPO files that may be used directly by ModelE
without dynamic ice sheets:

.. code-block:: bash

   cd twoway-discover/twoway/topo
   # TOPO file with global ECs, for uncoupled runs
   make topoa.nc

This creates the following files:

* ``topoa.nc``: May be used in a ModelE rundeck under the *TOPO* key.
  This files is on the ModelE atmosphere grid.

* ``topoa_nc4.nc``: Same as ``topoa.nc`` but in compressed NetCDF4 format,
  much smaller; ModelE input files must be NetCDF3.

* ``global_ecO.nc``: Contains the ``EvO`` matrix, which converts fields
  from the ModelE ocean grid to the ModelE elevation class on ocean
  grid.

* Other files starting in ``global_ecO.nc`` are temporary, and may be
  removed once the process is complete.

Other files of interest include:

* ``modele_ll_g1qx1.nc``: Grid definition file for ModelE ocean grid,
  for use with `Icebin <https://icebin.readthedocs.io>`_ regridding.


Coupled TOPO Files
``````````````````

To prepare for coupled runs, the following command will generate a *TOPO* file, on the ocean grid, with Greenland removed.

   # TOPO file missing Greenland, for coupled runs
   make topoo_ng.nc

Resulting files are:

* ``topoo_ng.nc``: Similar to ``topoa_nc4.nc``, but on the ocean grid and
  with Greenland removed.  The PISM version of Greenland will be used
  to replace it on the fly.

* ``global_ecO_ng.nc``: Like ``global_ecO.nc``, but with Greenland removed.

The files here will be used later, in combination with PISM state, to
produce ModelE boundary condition files.

Prepare Coupled ModelE Run
--------------------------

Not it is time to prepare input files for a coupled ModelE run:

#. Create a new run with a new rundeck.  The rundeck can be an
   existing rundeck, or taken straight from the templates.  Use the
   ``--nobuild`` flag to just set up the rundeck, do not try to build
   ModelE yet.  Eg:

   .. code-block:: bash

      cd ~/exp/mystudy
      ectl setup --nobuild --src ~/git/twoway-discover/modelE \
          --rundeck ~/git/twoway-discover/modelE/templates/E6F40.R \
          run1

#. If the rundeck uses non-Stieglitz ``GIC`` file (the default for
   templates), create a new Stieglitz-enabled ``GIC`` file:

   .. code-block:: bash

      cd ~/exp/mystudy/run1
      python3 ~/git/twoway/stieglitz/gic2stieglitz.py -d test1 GIC -o inputs/

   This program reads the runedeck used by *run1* to determine the
   *GIC* (global initial condition) file; and then creates a Stieglitz
   version of that file in ``run1/inputs/``.


#. Create merged TOPO and GIC files

   .. code-block:: bash

      cd ~/exp/mystudy
      python3 !~/git/twoway/topo/modele_pism_inputs.py --pism std-greenland/g20km_10ka.nc --grids grids --gic GIC.144X90.DEC01.1.ext_1.nc --run run1







python3 ~/git/twoway/topo/modele_pism_inputs.py --pism std-greenland/g20km_10ka.nc --grids grids --gic GIC.144X90.DEC01.1.ext_1.nc --run test1 2>x



Run ModelE Coupled
------------------

