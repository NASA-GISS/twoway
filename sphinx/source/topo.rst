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

The multi-step procedure can be summarized as follows:



