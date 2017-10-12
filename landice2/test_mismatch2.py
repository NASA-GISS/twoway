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
import itertools
import unittest

def compute_fcontO(mmO, sheetname):
    """Computes Continent land fractions, based on a single ice sheet.
    This prototype code will likely be converted to C++"""

    rmO = mmO.regrid_matrices(sheetname)

    # Regrid to fxoceanOp  (PISM fcont)
    OvI = rmO.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
    OvI_correct = rmO.matrix('AvI', scale=False, correctA=True)

    # Don't need to set up the mask on I ourselves; this is already
    # built into the OvI matrix.
    fcontI = np.ones(OvI.shape[1])

    # Full native area of Ocean grid cells.
    # Scaling for O grid cells (that we know about)
    # fill=1 ensures that grid cells we don't know about won't
    # be touched in the scaling matrix
    sO = 1. / mmO.wA('greenland', 'proj', fill=1.)

    # Convert O <- I
    fcontOp = sO * OvI.apply(fcontI, 0.)
    fcontOp = np.round(fcontOp, decimals=12)   # Why this?  Try without...

    # Round fcontOp (PISM) to get fcontOm (ModelE)
    fcontOm = np.round(fcontOp)

    return fcontOp, fcontOm


class MismatchTests(unittest.TestCase):

    def setUp(self):
        self.sheetname = 'greenland'
        self.mmO = icebin.GCMRegridder(args.icebin_in)

        with netCDF4.Dataset(args.icebin_in) as nc:
            self.indexingI = ibgrid.Indexing(nc, 'm.greenland.gridI.indexing')
            self.indexingA = ibgrid.Indexing(nc, 'm.gridA.indexing')
            self.indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
            self.hcdefs = nc.variables['m.hcdefs'][:]
            self.nhc = len(nc.dimensions['m.nhc'])
            indexA_sub = nc.variables['m.gridA.cells.index'][:]
            areaA_sub = nc.variables['m.gridA.cells.native_area'][:]
            nA1 = getattr(nc.variables['m.gridA.info'], 'cells.nfull')

        self.areaA1 = np.zeros((nA1,))
        self.areaA1[indexA_sub] = areaA_sub    # Native area of full grid cell (on sphere)


    def test_weight_sums(self):

        fcontOp, fcontOm = compute_fcontO(self.mmO, self.sheetname)

        # Construct a regridder to the Atmosphere grid
        mmA = self.mmO.to_modele(1.-fcontOp, 1.-fcontOm)
        rmA = mmA.regrid_matrices('greenland')

        wAAm, AAmvIp, wIp = rmA.matrix('AAmvIp', scale=True, correctA=False)()

        # -----------------------------
        rmO = self.mmO.regrid_matrices(self.sheetname)

        OvI = rmO.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
        wOvI,_,_ = OvI()

        OvI_correct = rmO.matrix('AvI', scale=False, correctA=True)
        wOvI_correct,_,_ = OvI_correct()
        # -----------------------------

        sum_wIp = np.nansum(wIp)
        sum_wOvI = np.nansum(wOvI)
        sum_wOvI_correct = np.nansum(wOvI_correct)
        sum_wAAm = np.nansum(wAAm)
        sum_fcontOp = np.sum(fcontOp * self.areaA1)
        sum_fcontOm = np.sum(fcontOm * self.areaA1)

        self.assertAlmostEqual(1.0, sum_wIp / sum_wOvI)
        self.assertAlmostEqual(1.0, sum_wOvI_correct / sum_fcontOp)
        self.assertAlmostEqual(1.0, sum_wAAm / sum_fcontOm)
                


        # Store for viewing
        with netCDF4.Dataset('test_weight_sums.nc', 'w') as nc:
            nc.createDimension('jmO', self.indexingA.shape[0])
            nc.createDimension('imO', self.indexingA.shape[1])
            nc.createDimension('nx', self.indexingI.shape[0])
            nc.createDimension('ny', self.indexingI.shape[1])
            nc.createDimension('jmA', self.indexingA.shape[0]/2)
            nc.createDimension('imA', self.indexingA.shape[1]/2)

            fcontOp_nc = nc.createVariable('fcontOp', 'd', ('jmO', 'imO'))
            fcontOm_nc = nc.createVariable('fcontOm', 'd', ('jmO', 'imO'))
            wIp_nc = nc.createVariable('wIp', 'd', ('nx', 'ny'))
            wAAm_nc = nc.createVariable('wAAm', 'd', ('jmA', 'imA'))

            fcontOp_nc[:] = fcontOp[:]
            fcontOm_nc[:] = fcontOm[:]
            wIp_nc[:] = wIp[:]
            wAAm_nc[:] = wAAm[:]






# ====================================================================

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

if __name__ == '__main__':
    args = parser.parse_args()
    unittest.main()
