.. _topo

topo/: Elevation-Class Enabled TOPO Files
=========================================

This project produces Elevation Class-enabled TOPO files for use in
ModelE.  By default, it produces one based on the following:

#. Ice elevations from ETOPO1.
#. Ice sheet extents (Greenland and Antarctica) from ETOPO1.
#. Ice fractions, other than ice sheets, from ``Z10MX10M`` input file.

A few notes:

#. This project is able to remove Greenland from the TOPO file, if
   needed, for use with two-coupling.  The current incarnation,
   intended for no coupling, leaves Greenland in place.

Running
-------

To run this project:

.. code-block:: console

   $ cd topo
   $ make topoa.nc

The multi-step procedure can be summarized as follows.  Note that ALL
output files are written in the current directory (``topo/``):

#. Convert some ModelE input files from class Fortran format to NetCDF.

#. Convert the (hand-drawn and compressed) Grenland Mask (included
   with this repository) to NetCDF.  This is used to optionally mask
   out Greenland when generating TOPO files, so a model-generated
   Greenland can be used in its place.  (Note that masking out
   Antarctica is easy by latitude).

#. Create a Greenland Mask on the ETOPO1 1-mintue grid.

#. Regenerate the ETOPO1 data with Greenland masked.

#. Generate a global map of 1-minute ice extent, ice elevation and
   ocean mask (``etopo1_ice_g1m.nc``).  This is the direct input to
   the elevation class generator.  Users wishing to generate elevation
   classes for other ice configurations should make an analog to this
   file using other techniques as appropriate.

#. Generate a classic TOPO file on the Ocean grid (``topoo.nc``)

#. Generate elevation class definitions (``glboal_ec_mm.nc``).  Note
   that these definitions can be used for any application requiring
   elevation classes; they are simply the regridding matrices between
   the GCM (Atmosphere), Ice and Elevation grids.

#. Generate an enhnaced TOPO file on the Atmosphere grid
   (``topoa.nc``).  Note that this must be in NetCDF classic
   (NetCDF 3) format for ModelE, which will read it using the
   ``pnetcdf`` system.

For more information, see documentation on:

* `IceBin <http://icebin.readthedocs.io>`_
