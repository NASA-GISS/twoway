.. TwoWay documentation master file, created by
   sphinx-quickstart on Wed May  9 22:54:34 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TwoWay: Coupled ModelE -- Ice Sheets
====================================

This document describes how to set up and run GISS
`ModelE <https://www.giss.nasa.gov/tools/modelE/>`_ with coupled
dynamic ice sheets via `PISM <https://pism-docs.org/>`_).  It ties
together work from a number of related modeling projects / repositories:

* *twoway* (this document; `repo <https://github.com/citibeth/twoway>`_):
  Top-level scripts / makefiles tying together other projects.  Used
  to generate input files for coupled runs.  Also serves as top-level
  HOWTO documentation.  Start reading here!

* `icebin <https://icebin.readthedocs.io>`_ (repos `icebin
  <https://github.com/citibeth/icebin>`_ and `ibmisc
  <https://github.com/citibeth.ibmisc>`_): Ice Sheet -- Atmosphere
  coupler.  Also includes regridding for elevation classes and Python
  interface for use in plotting results.

* `PISM <https://pism-docs.org/>`_ (`repo <https://github.com/pism/pism>`_): Parallel Ice Sheet Model

* `discover-docs <https://discover-docs.readthedocs.io>`_ (`repo
  <https://github.com/citibeth/discover-docs>`_): System-specific
  documentation for those using the `NCCS discover
  <https://nccs.nasa.gov>_` supercomputer.

.. toctree::
   :maxdepth: 2

   buildingrunning.rst
   twoway
