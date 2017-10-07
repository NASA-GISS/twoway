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
from modele.constants import SHI,LHM,RHOI,RHOS,UI_ICEBIN,UI_NOTHING
import scipy.sparse


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def load_icebin_in(fname, sheetname):
    """Loads an IceBin setup for the Ocean <--> Ice Grids"""
    ret = dict()

    mm = icebin.GCMRegridder(fname)
    rm = mm.regrid_matrices(sheetname)

    with netCDF4.Dataset(fname) as nc:
        indexingA = ibgrid.Indexing(nc, 'm.gridA.indexing')
        indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
        hcdefs = nc.variables['m.hcdefs'][:]
        nhc = len(nc.dimensions['m.nhc'])
        indexA_sub = nc.variables['m.gridA.cells.index'][:]
        areaA_sub = nc.variables['m.gridA.cells.native_area'][:]
        nA1 = getattr(nc.variables['m.gridA.info'], 'cells.nfull')

    areaA1 = np.zeros((nA1,))
    areaA1[indexA_sub] = areaA_sub    # Native area of full grid cell (on sphere)


    ret['mm'] = mm
    ret['rm'] = rm
    ret['indexingHC'] = indexingHC
    ret['indexingA'] = indexingA
    ret['hcdefs'] = hcdefs
    ret['nhc'] = nhc
    ret['areaA1'] = areaA1    # Native area of full grid cell

    return Struct(**ret)



parser = argparse.ArgumentParser(description='Produce elevation-classified input files')
#parser.add_argument('--topo-leaf', dest='topo',
#    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
#parser.add_argument('--gic-leaf', dest='gic',
#    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
parser.add_argument('--icebin-in', dest='icebin_in',
    default='pismsheet_g20_icebin_in.nc',
    help="Name of IceBin input file")
parser.add_argument('--elev-mask', dest='elev_mask',
    default='pismsheet_elev_mask.nc',
    help="name of elevation / mask file from the high-res ice sheet (extract of a PISM file).")
#parser.add_argument('--elev-mask-type', dest='elev_mask_type',
#    help="File type for elev-mask: pism, mar")
#parser.add_argument('--stieglitz', action='store_true', default=False,
#    help="Set to generate initial conditions for Stieglitz model")

args = parser.parse_args()

# --------------------------------
ibinO = load_icebin_in(args.icebin_in, 'greenland')

# Regrid to fxoceanOp  (PISM fcont)
OvI = ibinO.rm.matrix('AvI', scale=False, correctA=False)    # WeightedSparse

# Don't need to set up the mask on I ourselves; this is already
# built into the OvI matrix.
print('OvI.shape', OvI.shape)
fcontI = np.ones(OvI.shape[1])

# Scaling for O grid cells (that we know about)
# fill=1 ensures that grid cells we don't know about won't
# be touched in the scaling matrix
sO = 1. / ibinO.mm.wA('greenland', 'proj', fill=1.)

# Convert O <- I
fcontOp = sO * OvI.apply(fcontI, 0.)

# Round fcontOp (PISM) to get fcontOm (ModelE)
fcontOm = np.round(fcontOp)

# Store it for debugging viewing
fcontOp2 = fcontOp.reshape(ibinO.indexingA.shape)    # Row-major shape
fcontOm2 = fcontOm.reshape(ibinO.indexingA.shape)    # Row-major shape
with netCDF4.Dataset('x.nc', 'w') as nc:
    nc.createDimension('jm', ibinO.indexingA.shape[0])
    nc.createDimension('im', ibinO.indexingA.shape[1])
    fcontOp_nc = nc.createVariable('fcontOp', 'd', ('jm', 'im'))
    fcontOm_nc = nc.createVariable('fcontOm', 'd', ('jm', 'im'))

    fcontOp_nc[:] = fcontOp2[:]
    fcontOm_nc[:] = fcontOm2[:]

# Convert to focean
foceanOp = 1. - fcontOp
foceanOm = 1. - fcontOm


# Construct a regridder to the Atmosphere grid
ibinO.mm.to_modele(foceanOp, foceanOm)
mmA = ibinO.mm
ibinO = None

# ---------------------------------------------
rmA = mmA.regrid_matrices('greenland')
print('xxxxxxxxxxxxxxxx222')
wAAm, AAmvIp, wIp = rmA.matrix('AAmvIp', scale=True, correctA=False)()

print(wAAM.shape)
print(wIp.shape)
print(wAAm)
print(wIp)
