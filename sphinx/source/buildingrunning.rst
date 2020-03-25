.. _modele-pism:

Building / Running ModelE-PISM Coupled Model
============================================

These instructions outline how to set up a coupled ModelE-PISM on
*discover* (or any computer), starting from scratch.  For the most
part, command lines that can be cut-n-pasted into *discover* are used;
but many pathes can be changed to suit your needs as well.

* This tutorial assumes the use of the *bash* command shell.

Path Setup
----------

We assume the following paths.  The software may be installed in any
place; and the user may set these paths however they like.  These
environment variables do NOT need to be set to use this software,
they are merely set for the purposes of this tutorial.  However, if
you set these variables as appropriate in your shell now, you can
cut-n-paste from later parts of the tutorial.

.. code-block:: bash

   # Location of shared Spack instance containing installed
   # environment
   SPACK=~eafisch2/spack

   # Use this Environment spec within $SPACK
   # The environment needs to be tailored to your HPC system.
   SPENV=tw-discover12

   # Location of user's Spack harness
   HARNESS=~/harn/twh

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
   cd $SPACK
   # Don't worry about errors on this command
   source var/spack/environments/$SPENV/loads-x


Download Packages into Shared Spack Environment
```````````````````````````````````````````````

.. code-block:: bash

   cd $SPACK/var/spack/environments/$SPENV
   git clone git@github.com:citibeth/modele-control.git
   git clone git@github.com:citibeth/pygiss.git

Spack Compiler Configuration
````````````````````````````

Spack compiler definitions are in ``~/..spack/linux/compilers.yaml``.
Follow directions on `Compiler Configuration in the Spack Manual
<https://spack.readthedocs.io/en/latest/getting_started.html#compiler-configuration>`_.
Here is a sample used on *discover*.

.. code-block:: none
   # SLES12
   compilers:
   - compiler:
       environment: {}
       extra_rpaths: [/usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/compiler/lib/intel64_lin,/usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/mpi/intel64/lib]
       flags:
          cflags: -gcc-name=/usr/local/other/gcc/9.2.0/bin/gcc
          cxxflags: -gxx-name=/usr/local/other/gcc/9.2.0/bin/g++
       modules: []
       operating_system: suse_linux11
       paths:
         # https://software.intel.com/en-us/node/522750 
         cc: /usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/bin/intel64/icc
         cxx: /usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/bin/intel64/icpc
         f77: /usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/bin/intel64/ifort
         fc: /usr/local/intel/2020/compilers_and_libraries_2020.0.166/linux/bin/intel64/ifort
       spec: intel@20.0.166
       target: x86_64

.. note::

   The Intel compiler must be paird with an appropraite version of
   GCC.  See, for example, this `Discussion on Spack
   <https://github.com/spack/spack/issues/8356>`_.

Once you have configured your compiler, try building something simple.

.. code-block:: 

    $SPACK/bin/spack --no-env install zlib

If this works --- congratulations, you are ready to go with Spack!  If not... please contact the Spack community for help.  Here's what you will see if it worked:

.. code-block:: none

   do_install <spack.pkg.builtin.zlib.Zlib object at 0x7ffff185d190> None install_deps=True
   Installing zlib dependencies
   deps = []
   ==> Installing zlib
   ==> Searching for binary cache of zlib
   ==> Warning: No Spack mirrors are currently configured
   ==> No binary for zlib found: installing from source
   ==> Fetching http://zlib.net/fossils/zlib-1.2.11.tar.gz
   ######################################################################## 100.0%
   ==> Staging archive: /gpfsm/dnb53/eafisch2/spack/var/spack/stage/zlib-1.2.11-lk267u47ez67rkzl7z5gnrdqvhca2n46/zlib-1.2.11.tar.gz
   ==> Created stage in /gpfsm/dnb53/eafisch2/spack/var/spack/stage/zlib-1.2.11-lk267u47ez67rkzl7z5gnrdqvhca2n46
   ==> No patches needed for zlib
   ==> Building zlib [Package]
   ==> Executing phase: 'install'
   ==> Successfully installed zlib
     Fetch: 0.76s.  Build: 4.40s.  Total: 5.15s.
   [+] /gpfsm/dnb53/eafisch2/spack/opt/spack/linux-sles12-x86_64/intel-20.0.166/zlib-1.2.11-lk267u47ez67rkzl7z5gnrdqvhca2n46


Use Spack to Build Environement
```````````````````````````````

.. code-block:: bash

   $SPACK/bin/spack -e $SPENV concretize -f
   $SPACK/bin/spack -e $SPENV install
   cd $SPACK/var/spack/environments/$SPENV
   $SPACK/bin/spack -e $SPENV env loads -r
   sort loads | uniq >loads2
   cp loads2 loads

.. note::

   The Spack environment twoway-discover (``$SPENV``) is meant to work on the
   *NCCS Discover* supercomputer.  If this is being built on another
   system, then that environent should be copied, modified as
   appropriate for that system, checked in and submitted as a pull
   request.  Further details are out of the scope of this document;
   see `Spack Environments
   <https://spack.readthedocs.io/en/latest/environments.html>`_:

   .. code-block:: bash

      cd $SPACK/var/spack/environments
      cp -r twoway-discover twoway-mything
      nano twoway-mything/spack.yaml


Make Sure Spack is World Readable
`````````````````````````````````

When you are done building the prerequisite software, it is polite to
make it world readable for everyone, so others can use it too:

.. code-block:: bash

   chmod -R a+r $SPACK


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

   $SPACK/bin/spack -e $SPENV env harness -o $HARNESS

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

.. code-block:: bash

   git clone $SIMPLEX_USER@simplex.giss.nasa.gov:/giss/gitrepo/modelE.git -b e3/twoway
   cd $HARNESS/modelE; ln -s ../modele-setup.py .

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

For a typical HPC system, they can be set up by running the following,
which amends ``.bashrc``:

.. code-block:: bash

   cat <<EOF >>~/.bashrc
   # Where input files will be downloaded to if not found
   export MODELE_ORIGIN_DIR=$INPUT_FILES

   # Where to look for input files
   export MODELE_FILE_PATH=.:$INPUT_FILES
   EOF

After this is done, you may wish to look over / edit *.bashrc*.


Set up your SLURM Configuration
-------------------------------

Add lines to *.bashrc* by cut-n-paste the following interactively:

.. code-block:: bash

   cat <<EOF >>~/.bashrc
   # Controls how ModelE-Control launches jobs by default.
   export ECTL_LAUNCHER=slurm
   EOF

After this is done, you may wish to look over / edit *.bashrc*.

.. note::

   TODO: Move this configuration parameter into the `ectl.conf` file.


Run ModelE Standalone
---------------------

Now you are ready to run ModelE, as explained in `modele-control docs
<https://modele-control.readthedocs.io/en/latest/>`_.  Start by
creating a top-level *experiment* directory, which will house a number of
*studies*:

.. code-block:: sh

   mkdir $EXP
   echo >$EXP/ectl.conf   # Marks this as a project directory

Now you can create a *study directory*.  A study is a collection of
related ModelE *runs*:

.. code-block:: sh

   cd $EXP
   mkdir mystudy

Now you can create a ModelE *run*.  This command configures a run based on:

1. A ModelE source location (`--src` flag).
2. A ModelE rundeck (`--rundeck` flag).
3. The directory in which the run should be created (positional argument).

.. code-block:: sh

   cd $EXP/mystudy
   ectl setup --src $HARNESS/modelE --rundeck $HARNESS/modelE/templates/E6F40.R run1

Once the run directory has been created, the source and rundeck
locations don't need to be recreated.  You can just re-setup using one
of either:

.. code-block:: sh

   ectl setup run1
   cd run1; ectl setup .

Now you can run as follows.  Note that `-np` indicates the number of
cores to use.

.. code-block:: sh

   # Obtain number of physical cores on this machine (for this tutorial)
   ncpus=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
   corespercpu=$(grep "cpu cores" /proc/cpuinfo |sort -u |cut -d":" -f2)
   nproc=$((ncpus*corespercpu))

   # Short run of ModelE
   ectl run -ts 19491231,19500102 -np $nproc --time 00:10:00 --launcher slurm-debug run1

For more on running ModelE with ModelE-Control, see `ModelE-Control
Documentation <https://modele-control.readthedocs.io>`_.


Spinup PISM in Greenland
------------------------

These instuctions follow those in `PISM Docs
<https://pism-docs.org/sphinx/manual/std-greenland/index.html>`_ to
spin up a sample PISM ice sheet at *20km* resolution.  In this case,
we are making the PISM spin-up to be part of the study directory,
available for use by multiple ModelE-PISM runs.

.. code-block:: bash

   # Obtain number of physical cores on this machine (for this tutorial)
   ncpus=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
   corespercpu=$(grep "cpu cores" /proc/cpuinfo |sort -u |cut -d":" -f2)
   nproc=$((ncpus*corespercpu))

   # Spinup PISM
   cd $EXP/mystudy
   cp -r $HARNESS/pism/examples/std-greenland .
   cd std-greenland
   ./preprocess.sh nproc=$nproc
   export PISM_BIN=$(dirname $(which pismr))  # Spack Env set this wrong
   nice ./spinup.sh $nproc const 1000 20 sia g20km_10ka.nc

.. note::

   Normally, PISM jobs are run within a batch system.  This example
   simply runs on the local node, which is not always possible on HPC
   login nodes.  If your HPC system uses SLURM, you can run the PISM
   spinup via a command like:

   .. code-block:: bash
      sbatch --constraint=hasw --account=XXXX --ntasks=28 --time=0:01:01 --qos=debug <<EOF
      #!/bin/bash
      ./spinup.sh 28 const 1000 20 sia g20km_10ka.nc
      EOF



   Contact your system administrator for more info on SLURM in your
   local context..



EC-Enabled TOPO File
--------------------

This step generates boundary condition (TOPO) files for use with
ModelE. There are two levels: uncoupled TOPO files may be used diretly
by ModelE for uncoupled runs, whereas copuled TOPO files are used for
coupled runs.  You may choose to generate either or both.

Uncoupled General TOPO Files
````````````````````````````

The following generates TOPO files that may be used directly by ModelE
without dynamic ice sheets:

.. code-block:: bash

   cd $HARNESS/twoway/topo
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


.. code-block:: bash

   # TOPO file missing Greenland, for coupled runs
   make topoo_ng.nc

Resulting files are:

* ``topoo_ng.nc``: Similar to ``topoa_nc4.nc``, but on the ocean grid and
  with Greenland removed.  The PISM version of Greenland will be used
  to replace it on the fly.

* ``global_ecO_ng.nc``: Like ``global_ecO.nc``, but with Greenland removed.

The files here will be used later, in combination with PISM state, to
produce ModelE boundary condition files.

Create ModelE Run
-----------------

As with uncoupled ModelE, create a new run with a new rundeck.  The
rundeck can be an existing rundeck, or taken straight from the
templates, eg:

.. code-block:: bash

   cd $EXP/mystudy
   ectl setup --nobuild --src $HARNESS/modelE \
       --rundeck $HARNESS/modelE/templates/E6F40.R \
       run2

.. note::

   The ``--nobuild`` flag tells *ModelE-Control* to just set up the
   run directory, but do not try to build source code just yet.  For a
   coupled run, additional changes need to take palce before build
   happens.


Make ModelE Input Files
-----------------------

Coupled ModelE-PISM needs *TOPO* and *GIC* files in which:

* The observed ETOPO1 Greenland ice sheet is replaced with the model
  Greenland ice sheet from PISM.

* The *GIC* file is appropriate for the layering in the
  Lynch-Stieglitz snow/firn mode.

These file are generated by the command:

   .. code-block:: bash

      cd $EXP/mystudy
      python3 $HARNESS/twoway/topo/modele_pism_inputs.py \
          --pism std-greenland/g20km_10ka.nc \
          --grids grids --run run2

The following files are created in ``$EXP/mystudy/run2``, and used by
the ModelE rundeck:

* ``inputs/topoa.nc``: A *TOPO* file with elevation classes for all ice-covered
  land, and the Greenland ice sheet taken from PISM.

* ``inputs/GIC``: A *GIC* file suitable for the Lynch-Stieglitz
  layering, and based on the Greenland ice sheet taken from PISM.

The following files created in ``$EXP/mystudy/run2`` are used by the
IceBin coupler.  Note that IceBin needs to periodically regenerate the
*TOPO* file internally. Therefore, it needs the same input files as
``modele_pism_inputs.py``:

* ``config/icebin.cdl``: The IceBin configuration file, initialized with input files as appropriate.  Parameters fit broadly into three groups:

  #. Input files / output directories: These are pre-set to the
     correct values, based on files generated by this step

  #. IceBin parameters: The user might wish to change these

  #. PISM parameters: These are obtained from the PISM spinup
     operation.  The user might wish to change them; or else, use
     different parameters when spinning up PISM.

* ``inputs/gcmO.nc``: Definition of the grids used by this coupler:

  * *ModelE Ocean Grid*: Called the "atmosphere" grid in the comments

  * *Elevation Grid on ModelE Ocean*: Derived from ModelE Ocean Grid
    and defined elevation classes.

  * *Greenland Grid*: The local ice grid used by PISM; obtained from
    the PISM spinup file.

* ``inputs/topoo_ng.nc``: Global *TOPO* file, on ModelE Ocean Grid,
  but missing Greenland

* ``inputs/global_ecO_ng.nc``: *EvO*, missing Greenland.  *EvO*
  is a regridding matrix from the *ModelE Ocean Grid* (``O``) to the
  *Elevation Grid on ModelE Ocean* (``E``).



Rundeck Settings
----------------

Edit ``$EXP/mystudy/run2/rundeck.R``, make the following changes:

#. Add ``libpluggable`` to the *Components* section of the rundeck
   (``run2/rundeck.R``).  This will do the following:

   #. Builds the Fortran code inside ``<modelE>/model/lipluggable``.

   #. Adds the preprocessor symbol ``LIPLUGGABLE`` to the
      ``rundeck_opts.h`` file (only when using *ModelE-Control*)

#. If not using *ModelE-Control*, add the following line under
   *Preprocessor Options*:

   .. code-block:: C

      #define LIPLUGGABLE

#. Use the new ``GIC`` file created above:

   .. code-block:: none

      GIC=inputs/GIC    ! Alternate, use symlink

#. Use the new ``TOPO`` file created above:

   .. code-block:: none

      TOPO=inputs/topoa.nc


Run ModelE
----------

Re-run setup to finish setting up a run, including building ModelE:

.. code-block::

   cd $EXP/mystudy
   ectl setup test1

At this point, coupled ModelE may be run the same as uncoupled ModelE
above, for example:

.. code-block::

   # Obtain number of physical cores on this machine (for this tutorial)
   ncpus=$(grep "physical id" /proc/cpuinfo | sort -u | wc -l)
   corespercpu=$(grep "cpu cores" /proc/cpuinfo |sort -u |cut -d":" -f2)
   nproc=$((ncpus*corespercpu))

   # Short run of ModelE
   cd $EXP/mystudy
   ectl run -ts 19491231,19500102 -np $nproc --time 00:10:00 --launcher slurm-debug run2


Log Files
`````````


Coupled Output Files
````````````````````

In addition to output files normally written by uncoupled ModelE, the following output is generated...


Coupled Restart Files
`````````````````````
