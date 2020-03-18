.. _modele-pism:

Building / Running ModelE-PISM Coupled Model
============================================

These instructions outline how to set up a coupled ModelE-PISM on
*discover* (or any computer), starting from scratch.  For the most
part, command lines that can be cut-n-pasted into *discover* are used;
but many pathes can be changed to suit your needs as well.

Build the Spack Environment
---------------------------

This builds the prerequisite software.  It only needs to be done once
by *someone*.  If you are not `eafisch2`, it has probably already been
done, and this is just for future reference.

Check out Spack
```````````````

It doesn't have to be in `~eafisch2/spack7`, you can put Spack wherever you like.

.. code-block:: bash

   cd ~eafisch2
   git@github.com:citibeth/spack.git -b efischer/giss2 spack7


Use Spack to Build Environement
```````````````````````````````

.. code-block:: bash

   ~eafisch2/spack7/bin/spack -e twoway-discover concretize -f
   ~eafisch2/spack7/bin/spack -e twoway-discover install
   ~eafisch2/spack7/bin/spack -e twoway-discover env loads -r
   pushd /gpfsm/dnb53/eafisch2/spack7/var/spack/environments/twoway-discover-latest
   sort loads | uniq >loads2
   cp loads2 loads


Set up your own Harness on the Spack Environment
------------------------------------------------

The Spack Environemnt above consists of all prerequisite packages,
plus a small number of packages you will build yourself.  A *Spack
Harness* consists of CMake setup scripts that use the Spack
Environment, but allow you to build your packages in your own private
location.  You can create as many harnesses as you like, for as many
checkouts / clones of the software as you like.


Start by creating the harness.  Note that you can put the harness in
any location you like, not just in `~/git`.  And you can name the
harness folder anything you like (the `-o` flag below):

.. code-block:: bash
   
   ~eafisch2/spack7/bin/spack -e twoway-discover env harness -o twoway-discover
   cd twoway-discoer

Load your Spack Environment
```````````````````````````

This needs to be done every time you log in or start a new shell.  You
might want to put it in your `.bashrc` file:

.. code-block:: bash

   source ~/git/twoway-discover/loads-x


Clone Your Software
-------------------

Now clone the software you need:

.. code-block:: bash

   git clone git@github.com:citibeth/ibmisc.git
   git clone git@github.com:citibeth/icebin.git
   git clone git@github.com:citibeth/twoway.git
   git clone git@github.com:pism/pism.git -b efischer/dev


At this point you can clone ModelE.  You may wish to clone it multiple
times into multiple directories, based on different branches.

   git clone <username>@simplex.giss.nasa.gov:/giss/gitrepo/modelE.git -b e3/twoway
   cd modelE; ln -s ../modele-setup.py .; cd ..

.. note::

   Cloning ModelE requires you have an account on *simplex*.  Replace
   `<username>` with your Simplex username.

Build the Software
------------------

It should be built in the order: *ibmisc*, *icebin*, *pism*.  The first three are all built the same way:

.. code-block:: bash

   cd ibmisc
   mkdir build
   cd build
   python3 ../../ibmisc-setup.py ..
   make install -j20
   cd ..

.. code-block:: bash

   cd icebin
   mkdir build
   cd build
   python3 ../../icebin-setup.py ..
   make install -j20
   cd ..


.. code-block:: bash

   cd pism
   mkdir build
   cd build
   python3 ../../pism-setup.py ..
   make install -j20
   cd ..

To clean a build:

.. code-block:: bash

   # rm -rf ibmisc/build

In the future, if you edit any of these packages, you will need to
rebuild them.  If you edit header files in *ibmisc*, you will also
need to rebuild *icebin*.

Set up ModelE Input Files
-------------------------

TODO: This feature is not useful and too complex.

.. code-block:: bash

   cd ~/nobackup
   mkdir modele_inputs
   cd modele_inputs
   mkdir local
   # For NCCS discover:
   ln -s /discover/nobackup/projects/giss/prod_input_files origin
   # For outside of NCCS:
   mkdir origin

Add to *.bashrc*:

.. code-block:: bash

   # Where to look for input files
   export MODELE_FILE_PATH=.:$HOME/nobackup/modele_inputs/origin:$HOME/nobackup/modele_inputs/local
   # Where input files will be downloaded to if not found
   export MODELE_ORIGIN_DIR=$HOME/nobackup/modele_inputs/origin

Set up your SLURM Configuration
-------------------------------

Add to *.bashrc*:

.. code-block:: bash

   export ECTL_LAUNCHER=slurm


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
