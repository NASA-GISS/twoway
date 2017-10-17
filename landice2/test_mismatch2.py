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
import contextlib

def get_fcontOp(mmO, OvI):
    # Don't need to set up the mask on I ourselves; this is already
    # built into the OvI matrix.  The mask, taken from PISM, includes
    # all bare land and ice-covered areas.
    # See: pygiss/giss/pism.py   _get_landmask()
    #    (used by write_icebin_in_base.py)
    fcontI = np.ones(OvI.shape[1])

    # Full native area of Ocean grid cells.
    # Scaling for O grid cells (that we know about)
    # fill=1 ensures that grid cells we don't know about won't
    # be touched in the scaling matrix
    sO = 1. / mmO.wA('greenland', 'proj', fill=1.)

    # Convert O <- I
    fcontOp = sO * OvI.apply(fcontI, 0.)
    fcontOp = np.round(fcontOp, decimals=12)   # Why this?  Try without...

    return fcontOp

def compute_fcontO(mmO, sheetname):
    """Computes Continent land fractions, based on a single ice sheet.
    This prototype code will likely be converted to C++"""

    # ----------------------------------------------------------------
    # Create a special regridder with elevI set according to the
    # ice+land mask, instead of the default ice mask.  This allows
    # us to compute fcont (instead of fgice)

    #     See pism/src/base/util/Mask.hh
    #     enum MaskValue {
    #       MASK_UNKNOWN          = -1,
    #       MASK_ICE_FREE_BEDROCK = 0,
    #       MASK_GROUNDED         = 2,
    #       MASK_FLOATING         = 3,
    #       MASK_ICE_FREE_OCEAN   = 4
    #     };
    with netCDF4.Dataset(args.elev_mask) as nc:
        maskI = np.array(nc.variables['mask'][:], dtype=np.int32)[0,:,:]
        maskI = np.where(
            np.logical_or(maskI==2,maskI==3,maskI==0),np.int32(0),np.int32(1)).reshape(-1)
        thkI = nc.variables['thk'][:].reshape(-1)
        topgI = nc.variables['topg'][:].reshape(-1)
    elevI = thkI + topgI
    elevI[~maskI] = np.nan

    mmO = icebin.GCMRegridder(args.icebin_in)
    mmO.set_elevI(sheetname, elevI)
    # ----------------------------------------------------------------

    rmO = mmO.regrid_matrices(sheetname)

    # Regrid to fxoceanOp  (PISM fcont)
    OvI = rmO.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
    OvI_correct = rmO.matrix('AvI', scale=False, correctA=True)


    fcontOp = get_fcontOp(mmO, OvI)

    # Round fcontOp (PISM) to get fcontOm (ModelE)
    fcontOm = np.round(fcontOp)

    return fcontOp, fcontOm


class MismatchTests(unittest.TestCase):

    """Tests GCMRegridder_ModelE, where the ice sheet is mismatched
    between GCM and Dynamic Ice Model."""

    def setUp(self):
        self.sheetname = 'greenland'
        self.mmO = icebin.GCMRegridder(args.icebin_in)

        rmO = self.mmO.regrid_matrices(self.sheetname)
        OvI = rmO.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
        _,_,self.wI = OvI()

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

        self.fcontOp, self.fcontOm = compute_fcontO(self.mmO, self.sheetname)

        # Construct a GCMRegridder_Model to/from the Atmosphere Grid
        self.mmA = self.mmO.to_modele(1.-self.fcontOp, 1.-self.fcontOm)


    def assert_equal_np(self, A, B):
        for ix,(a,b) in enumerate(zip(A,B)):
            ratio = a/b
            if not np.isnan(ratio):
                try:
                    self.assertAlmostEqual(1.,ratio, msg='ix={}'.format(ix))
                    pass
                except:
                    print('A={}, B={}'.format(a,b))
                    raise


    @contextlib.contextmanager
    def new_nc(self, fname):
        with netCDF4.Dataset(fname, 'w') as nc:
            nc.createDimension('jmO', self.indexingA.shape[0])
            nc.createDimension('imO', self.indexingA.shape[1])
            nc.createDimension('nx', self.indexingI.shape[0])
            nc.createDimension('ny', self.indexingI.shape[1])
            nc.createDimension('jmA', self.indexingA.shape[0]/2)
            nc.createDimension('imA', self.indexingA.shape[1]/2)
            nc.createDimension('nhc', self.nhc)

            yield nc


    def xtest_weight_sums(self):

        rmA = self.mmA.regrid_matrices(self.sheetname)
        wAAm, AAmvIp, wIp = rmA.matrix('AAmvIp', scale=True, correctA=False)()

        # -----------------------------
        rmO = self.mmO.regrid_matrices(self.sheetname)

        OvI = rmO.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
        wOvI,_,_ = OvI()

        OvI_correct = rmO.matrix('AvI', scale=False, correctA=True)
        wOvI_correct,_,_ = OvI_correct()
        # -----------------------------

        # Calculate fgiceOm from fgiceOp, fcontOp, fcontOm
        fgiceOp = get_fcontOp(self.mmO, OvI)
        fgiceOm = self.fcontOm * (fgiceOp / self.fcontOp)
        fgiceOm[np.isnan(fgiceOm)] = 0.

        sum_wIp = np.nansum(wIp)
        sum_wOvI = np.nansum(wOvI)
        sum_wOvI_correct = np.nansum(wOvI_correct)
        sum_wAAm = np.nansum(wAAm)
        sum_fgiceOp = np.sum(fgiceOp * self.areaA1)
        sum_fgiceOm = np.sum(fgiceOm * self.areaA1)

        self.assertAlmostEqual(1.0, sum_wIp / sum(self.wI))
        self.assertAlmostEqual(1.0, sum_wIp / sum_wOvI)
        self.assertAlmostEqual(1.0, sum_wOvI_correct / sum_fgiceOp)
        self.assertAlmostEqual(1.0, sum_wAAm / sum_fgiceOm)
                


        # Store for viewing
        with self.new_nc('test_weight_sums.nc') as nc:
            fcontOp_nc = nc.createVariable('fcontOp', 'd', ('jmO', 'imO'))
            fcontOm_nc = nc.createVariable('fcontOm', 'd', ('jmO', 'imO'))
            wIp_nc = nc.createVariable('wIp', 'd', ('nx', 'ny'))
            wAAm_nc = nc.createVariable('wAAm', 'd', ('jmA', 'imA'))

            fcontOp_nc[:] = self.fcontOp[:]
            fcontOm_nc[:] = self.fcontOm[:]
            wIp_nc[:] = wIp[:]
            wAAm_nc[:] = wAAm[:]

    # -----------------------------------------------------
    # -----------------------------------------------------
    # Sample functions

    def diagonalI(self):
        shapeI = self.indexingI.shape
        valI = np.zeros(shapeI)
        for i in range(0,shapeI[0]):
            for j in range(0,shapeI[1]):
                valI[i,j] = i + j
        return valI.reshape(-1)

    def constantI(self):
        valI = np.zeros(self.indexingI.shape) + 1
        return valI.reshape(-1)

    def elevationI(self):
        with netCDF4.Dataset(args.elev_mask) as nc:
            maskI = np.array(nc.variables['mask'][:], dtype=np.int32)[0,:,:]
            maskI = np.where(
                np.logical_or(maskI==2,maskI==3,maskI==0),np.int32(0),np.int32(1)).reshape(-1)
            thkI = nc.variables['thk'][:].reshape(-1)
            topgI = nc.variables['topg'][:].reshape(-1)
        elevI = thkI + topgI
        elevI[~maskI] = np.nan
        return elevI
    # -----------------------------------------------------

    def assert_eq_weighted(self, A, wA, B, wB):
        Asum = np.nansum(np.multiply(A, wA))
        Bsum = np.nansum(np.multiply(B, wB))
        self.assertAlmostEqual(1., Asum/Bsum)


    def test_conserv(self):
        """Tests conservation of mass.  Checks that the amount of
        stuff (== value * weight) remains constant."""


        # Indices we worry about (i + j*144)
        ixs = [50 + 80*144, 46 + 82*144, 57 + 86*144]


        rmA = self.mmA.regrid_matrices(self.sheetname)
        AAmvIp = rmA.matrix('AAmvIp', scale=True, correctA=False)
        wAAm,_,wIp = AAmvIp()

        EAmvIp = rmA.matrix('EAmvIp', scale=True, correctA=False)
        wEAm,M,wIp2 = EAmvIp()

        # Total area of grid cells; should be approximately the same
        print('wIp', np.nansum(wIp))
        print('wAAm', np.nansum(wAAm))
        print('wEAm', np.nansum(wEAm))

        self.assertAlmostEqual(1., np.nansum(wEAm) / np.nansum(wAAm));
        self.assert_equal_np(wIp, wIp2)


        for fname,valIp_fn in (('diagonal', self.diagonalI), ('constant', self.constantI), ('elevation', self.elevationI)):
            valIp = valIp_fn()

            # A <--> I
            valAAmIp = AAmvIp.apply(valIp, fill=np.nan, force_conservation=True)
            self.assertAlmostEqual(1.0, np.nansum(wAAm * valAAmIp) / np.nansum(wIp * valIp))


            # E <--> I
            valEAmIp = EAmvIp.apply(valIp, fill=np.nan, force_conservation=True)
            print('valEAmIp', np.nansum(wEAm * valEAmIp), np.nansum(wIp * valIp))
            self.assertAlmostEqual(1.0, np.nansum(wEAm * valEAmIp) / np.nansum(wIp * valIp))

#            print('ZR valAAmIp', valAAmIp[ixs])
#            print('ZR wAAm', wAAm[ixs])
#            print('ZR sum', np.nansum(wAAm * valAAmIp), np.nansum(wIp * valIp))

#            valAAmIp /= wAAm
#            self.assert_eq_weighted(valIp, wIp, valAAmIp, wAAm)


            with self.new_nc('mismatch_' + fname + '.nc') as nc:
                valIp_nc = nc.createVariable('valIp', 'd', ('nx', 'ny'))
                wAAm_nc = nc.createVariable('wAAm', 'd', ('jmA', 'imA'))
                wEAm_nc = nc.createVariable('wEAm', 'd', ('nhc', 'jmA', 'imA'))
                valAAmIp_nc = nc.createVariable('valAAmIp', 'd', ('jmA', 'imA'))
                valEAmIp_nc = nc.createVariable('valEAmIp', 'd', ('nhc', 'jmA', 'imA'))

                valIp_nc[:] = valIp[:]
                wAAm_nc[:] = wAAm[:]
                wEAm_nc[:] = wEAm[:]
                valAAmIp_nc[:] = valAAmIp[:]
                valEAmIp_nc[:] = valEAmIp[:]




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
