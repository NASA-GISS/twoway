import os
srcdir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(srcdir, '..', '..', 'python', 'lib'))

import copy
import numpy as np
from giss import giutil
import icebin
from icebin import ibgrid
from giss.ncutil import copy_nc
import netCDF4
import argparse
#from modele.constants import SHI,LHM,RHOI,RHOS,UI_ICEBIN,UI_NOTHING

# Sample program that tries out IceBin's update_topo() and writes the output to NetCDF.
# The filder ../make_topo must have been run first, for the file z1qx1n_bs1-nogr.nc

file_path = os.environ['MODELE_FILE_PATH'].split(os.pathsep)
TOPOO_IN = giutil.search_file('z1qx1n_bs1-nogr.nc', file_path)
ICEBINO_IN = 'pismsheet_g20_icebin_in.nc'
ELEVMASK_IN = 'pismsheet_elev_mask.nc'

# ---------------------------------------
# Read dimensions
with netCDF4.Dataset(ICEBINO_IN) as nc:
    indexingO = ibgrid.Indexing(nc, 'm.gridA.indexing')
    indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
    hcdefs_ice = nc.variables['m.hcdefs'][:]
    nhc_ice = len(nc.dimensions['m.nhc'])

im = indexingO.extent[0] // 2    # Indices in alphabetical order
jm = indexingO.extent[1] // 2    # /2 to convert Ocean to Atmosphere grid

segments = 'legacy,sealand,ec'
nhc_gcm = nhc_ice + 3
# ---------------------------------------


# Create gcmO and wrap to get gcmA.  Not yet usable, we haven't done
# anything about foceanAOp or foceanAOm yet.
mmA = icebin.GCMRegridder(ICEBINO_IN).to_modele()

# Allocate arryas for update_topo to write into.
# In ModelE, these are allocated by the GCM.
fhc = np.zeros((nhc_gcm,jm,im), dtype='d')
underice = np.zeros((nhc_gcm,jm,im), dtype='i')
elevE = np.zeros((nhc_gcm,jm,im), dtype='d')

focean = np.zeros((jm,im), dtype='d')
flake = np.zeros((jm,im), dtype='d')
fgrnd = np.zeros((jm,im), dtype='d')
fgice = np.zeros((jm,im), dtype='d')
zatmo = np.zeros((jm,im), dtype='d')
foceanOm0 = np.zeros((jm,im), dtype='d')

# ---------------------------------------------------------
with netCDF4.Dataset(ELEVMASK_IN) as nc:
    thkI = nc.variables['thk'][:].reshape(-1)
    topgI = nc.variables['topg'][:].reshape(-1)
    maskI = nc.variables['mask'][:].reshape(-1)

elevI = topgI + thkI
# ---------------------------------------------------------
sigma = (50000., 50000., 1000.)
elevmask_sigmas = {'greenland' : (elevI, maskI, sigma)}
mmA.update_topo(
    TOPOO_IN, elevmask_sigmas, False,
    segments,
    fhc, underice, elevE,
    focean, flake, fgrnd, fgice, zatmo, foceanOm0)


# ---------------------------------------------------------

with netCDF4.Dataset('TOPOA.nc', 'w') as nc:
    nc.createDimension('nhc', nhc_gcm)
    nc.createDimension('jm', jm)
    nc.createDimension('im', im)

    fhc_v = nc.createVariable('fhc', 'd', (nhc_gcm,jm,im), zlib=True)
    underice_v = nc.createVariable('underice', 'i', (nhc_gcm,jm,im), zlib=True)
    elevE_v = nc.createVariable('elevE', 'd', (nhc_gcm,jm,im), zlib=True)

    focean_v = nc.createVariable('focean', 'd', (jm,im), zlib=True)
    flake_v = nc.createVariable('flake', 'd', (jm,im), zlib=True)
    fgrnd_v = nc.createVariable('fgrnd', 'd', (jm,im), zlib=True)
    fgice_v = nc.createVariable('fgice', 'd', (jm,im), zlib=True)
    zatmo_v = nc.createVariable('zatmo', 'd', (jm,im), zlib=True)
    foceanOm0_v = nc.createVariable('foceanOm0', 'd', (jm,im), zlib=True)


    fhc_v[:] = fhc
    underice_v[:] = underice
    elevE_v[:] = elevE

    focean_v[:] = focean
    flake_v[:] = flake
    fgrnd_v[:] = fgrnd
    fgice_v[:] = fgice
    zatmo_v[:] = zatmo
    foceanOm0_v[:] = foceanOm0


