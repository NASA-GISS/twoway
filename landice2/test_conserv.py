# IceBin: A Coupling Library for Ice Models and GCMs
# Copyright (c) 2013-2016 by Elizabeth Fischer
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import scipy.sparse
import itertools

import icebin
from icebin import ibgrid, ibplotter
import matplotlib
#import basemap
import numpy as np
import netCDF4
import pickle
import sys
import giss.basemap
#import giss.modele
from modele import deprecated_plot_params
import giss.plot
import giss.pism

#ice_sheet = 'greenland'
#ICEBIN_IN = 'icebin_in.nc'

regrid_names = ('IvA', 'AvI', 'IvE', 'EvI', 'EvA', 'AvE')

def diag_matrix(vec):
    """Turns a dense vector into a sparse diagonal matrix"""
    vec_2 = vec.reshape(1,len(vec))
    dia = scipy.sparse.dia_matrix((vec_2, [0]), shape=(len(vec), len(vec)))
    return dia


class RegridTests(unittest.TestCase):

    def setUp(self):
        print('BEGIN RegridTests.setUp(): ', ICEBIN_IN)
        self.elevI, self.maskI = giss.pism.read_elevI_maskI(ELEV_MASK)
        self.elevmaskI = self.elevI
        self.elevmaskI[self.maskI] = np.nan

        self.mm = icebin.GCMRegridder(ICEBIN_IN)
        self.rm = self.mm.regrid_matrices(ice_sheet, self.elevmaskI)
		# Smooth 50km in XY direction, 100m in Z direction
        sigma=(50000., 50000., 100.)
        self.wIvE,self.IvE,self.IvEw = self.rm.matrix('IvE', scale=True, sigma=sigma)()

        self.wAvI,self.AvI,self.AvIw = self.rm.matrix('AvI', scale=True)()
        self.wIvA,self.IvA,self.IvAw = self.rm.matrix('IvA', scale=True)()
        self.wEvI,self.EvI,self.EvIw = self.rm.matrix('EvI', scale=True)()
        self.wIvE,self.IvE,self.IvEw = self.rm.matrix('IvE', scale=True)()
        self.wIvE,self.IvE,self.IvEw = self.rm.matrix('IvE', scale=True)()
        self.wEvA,self.EvA,self.EvAw = self.rm.matrix('EvA', scale=True)()
        self.wAvE,self.AvE,self.AvEw = self.rm.matrix('AvE', scale=True)()

        self.IvE_smooth_x = self.rm.matrix('IvE', scale=True, sigma=sigma)

        with netCDF4.Dataset(ICEBIN_IN) as nc:
            self.indexingA = ibgrid.Indexing(nc, 'm.agridA.indexing')
            self.indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
            self.indexingI = ibgrid.Indexing(nc, 'm.{}.agridI.indexing'.format(ice_sheet))
            self.plotterI = ibplotter.read_nc(nc, 'm.{}.agridI'.format(ice_sheet))
            self.plotterA = ibplotter.read_nc(nc, 'm.agridA')
        self.plotterE = ibplotter.PlotterE(ICEBIN_IN, ice_sheet, IvE=self.IvE)

        print('END RegridTests.setUp()')




    # -----------------------------------------------------
    def assert_equal_sparse(self, rname, _A, _B, msg=''):
        print('Regrid {}:'.format(rname))
        A = scipy.sparse.coo_matrix(_A)
        B = scipy.sparse.coo_matrix(_B)

        At = sorted(zip(A.row, A.col, A.data))
        Bt = sorted(zip(B.row, B.col, B.data))

        for a,b in zip(At,Bt):
            self.assertEqual(a[0:2],b[0:2],msg=msg)
            self.assertAlmostEqual(1.,a[2]/b[2],msg=msg)

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

    # -----------------------------------------------------
    def run_weights(self, rname, correctA):
        print('*** run_weights', rname, correctA)
        msg = '{}-{}'.format(rname, correctA)
        wB_S, BvA_S, wA_S = self.rm.matrix(rname, scale=True, correctA=correctA)()
        wB_s, BvA_s, wA_s = self.rm.matrix(rname, scale=False, correctA=correctA)()

        # Weight should not depend on whether or not we chose a scaled matrix
        # In fact, the same code should produce weights either way, so we
        # can use exact FP equality in this test.
        for i in range(0,len(wB_S)):
            if wB_s[i] == wB_S[i]:
                continue
            print('   --> weight difference[%d]: %g %g' % (i,wB_S[i], wB_s[i]))
        self.assertTrue(np.all(wB_S == wB_s), msg=msg)

        # Weights convert a scaled matrix to an unscaled matrix
        # Invariant: <weights> * <scaled-M> == <unscaled-M>
        self.assert_equal_sparse(rname, BvA_s, diag_matrix(wB_S) * BvA_S, msg=msg)

    def test_weights(self):
        """Check that the weighted and unweighted versions of the
        matrices are consistent with the weight vectors.
             We should have:   BvA = wBvA * BvA(SCALED)"""

        # ('IvA', 'AvI', 'IvE', 'EvI', 'EvA', 'AvE')
        for rname in regrid_names:
            for correctA in (False,True):
                self.run_weights(rname, correctA=correctA)

    def test_total_area(self):
        """Check that sum(wAvB) == sum(wBvA)"""
        errs = []
        for scale in (False,True):
            for correctA in (False, True):
                for (nAvB,nBvA) in zip(regrid_names[::2], regrid_names[1::2]):
                    wAvB,_,AvBw = self.rm.matrix(nAvB, scale=scale, correctA=correctA)()
                    wBvA,_,BvAw = self.rm.matrix(nBvA, scale=scale, correctA=correctA)()
                    self.assertNotEqual(wAvB.shape, wBvA.shape)

                    if np.any(np.abs(wAvB / BvAw - 1.0) > 1.e-7):
                        err = '1. w{} vs. {}w, correctA={} scale={} ratio={}'.format(
                            nAvB, nBvA, correctA, scale, ratio)
                        errs.append(err)
                        print(err)

                    if np.any(np.abs(AvBw / wBvA - 1.0) > 1.e-7):
                        err = '2. {}w vs. w{}, correctA={} scale={} ratio={}'.format(
                            nAvB, nBvA, correctA, scale, np.nanmean(AvBw / wBvA))
                        errs.append(err)
                        print(err)

                    # This will only work when not correctA.
                    # The vector wAvB always representees the "area" of the A
                    # grid cells.  If correctA=True, then wIvE will represent
                    # the area of grid cells on a Cartesian plane; but wEvI
                    # will represent the area of similar cells on the sphere.
                    # The two will be different.
                    if not correctA:
                        ratio = sum(wAvB)/sum(wBvA)
                        if (abs(1.-ratio) > 1.e-7):
                            err = '3. {} vs. {}, correctA={} scale={} ratio={}'.format(
                                nAvB, nBvA, correctA, scale, ratio)
                            errs.append(err)
                            print(err)

        if len(errs) > 0:
            self.assertTrue(False, msg='\n    '+'\n    '.join(errs))

    # -----------------------------------------------------
    def run_plot_weights(self, rname):
        grid = rname[0]
        if (grid == 'A'):
            plotter = self.plotterA
        elif (grid == 'E'):
            plotter = self.plotterE
        elif (grid == 'I'):
            plotter = self.plotterI


        wB_C, BvA_C, wA_C = self.rm.matrix(rname, scale=True, correctA=True)()
        wB_c, BvA_c, wA_c = self.rm.matrix(rname, scale=True, correctA=False)()

        wBvA_C = np.squeeze(np.asarray(BvA_C.sum(axis=1)))    # sum rows
        wBvA_c = np.squeeze(np.asarray(BvA_c.sum(axis=1)))    # sum rows


        figure = matplotlib.pyplot.figure(figsize=(11,17))

        ax = figure.add_subplot(221)
        basemap = giss.basemap.greenland_laea(ax=ax)
        giss.plot.plot_var(ax=ax, basemap=basemap,
            **deprecated_plot_params.plot_params(
                'weight-%s (corrected)' % rname,
                val=wB_C, plotter=plotter))

        ax = figure.add_subplot(222)
        basemap = giss.basemap.greenland_laea(ax=ax)
        giss.plot.plot_var(ax=ax, basemap=basemap,
            **deprecated_plot_params.plot_params(
                'computed weight-%s (corrected)' % rname,
                val=wBvA_C, plotter=plotter))


        ax = figure.add_subplot(223)
        basemap = giss.basemap.greenland_laea(ax=ax)
        giss.plot.plot_var(ax=ax, basemap=basemap,
            **deprecated_plot_params.plot_params(
                'weight-%s (ratio: corrected/uncorrected)' % rname,
                val=np.divide(wB_C,wB_c), plotter=plotter))

        ax = figure.add_subplot(224)
        basemap = giss.basemap.greenland_laea(ax=ax)
        giss.plot.plot_var(ax=ax, basemap=basemap,
            **deprecated_plot_params.plot_params(
                'computed weight-%s (ratio: corrected/uncorrected)' % rname,
                val=np.divide(wBvA_C, wBvA_c), plotter=plotter))

        figure.savefig('%s-weight' % rname, dpi=70, transparent=False)

    def test_plot_weights(self):
        """Check that the weighted and unweighted versions of the
        matrices are consistent with the weight vectors.
             We should have:   BvA = wBvA * BvA(SCALED)"""

        # ('IvA', 'AvI', 'IvE', 'EvI', 'EvA', 'AvE')
        for rname in regrid_names:
            self.run_plot_weights(rname)
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
        return self.elevI.reshape(-1)

    # -----------------------------------------------------

    def test_constant_regrid(self):
        """Regrid the constant function, check that answer is always
        what we started with."""

        valI = self.constantI()

        # A <-- I
        valAI = icebin.coo_multiply(self.AvI, valI, fill=np.nan)        # Most recent space is on the left
        valIAI = icebin.coo_multiply(self.IvA, valAI, fill=np.nan)      # Read history right-to-left.
        self.assert_equal_np(valI, valIAI)

        # Make sure A<--I DOES have projection scaling
        # Look at valAI, make sure it's not all the same
        x = valAI - 1
        xsum = np.nansum(x*x)
        # This will be 0 if valAI is 1 everywhere, non-zero if valAI varies.
        # valAI should vary because the projection used (Stereographic) is non-area-preserving.
        self.assertNotEqual(0., xsum)
            

        # E <-- I
        valEI = icebin.coo_multiply(self.EvI, valI, fill=np.nan)        # Most recent space is on the left
        valIEI = icebin.coo_multiply(self.IvE, valEI, fill=np.nan)      # Read history right-to-left.
        self.assert_equal_np(valI, valIEI)

        # A <-- E
        valE = np.zeros(len(self.indexingHC)) + 1
        valE = valE.reshape(-1)

        valAE = icebin.coo_multiply(self.AvE, valE, fill=np.nan)        # Most recent space is on the left
        valEAE = icebin.coo_multiply(self.EvA, valAE, fill=np.nan)      # Read history right-to-left.
        self.assert_equal_np(valE, valEAE)

        # Make sure A<-E and E<-A have no net projection scaling
        valA = np.zeros(len(self.indexingA)) + 1
        valA = valA.reshape(-1)
        valEA = icebin.coo_multiply(self.EvA, valA, fill=np.nan)
        valAEA = icebin.coo_multiply(self.AvE, valEA, fill=np.nan)
        self.assert_equal_np(valA, valAEA)
        self.assert_equal_np(valA, valAE)
        self.assert_equal_np(valEA, valE)

    def assert_eq_weighted(self, A, wA, B, wB):
        Asum = np.nansum(np.multiply(A, wA))
        Bsum = np.nansum(np.multiply(B, wB))
        self.assertAlmostEqual(1., Asum/Bsum)


    def test_apply(self):
        # Get a matrix and 2 vector; we will apply to both simultaneously
        AvI_x = self.rm.matrix('AvI', scale=True)
        valI = np.stack((self.elevationI(), self.diagonalI()))
        nvar = valI.shape[0]

        # Method 1: coo_multiply
        wAvI,AvI,AvIw = AvI_x()
        valA1 = list()
        print('nvar',nvar)
        for i in range(0,nvar):
            valA1.append(icebin.coo_multiply(AvI, valI[i,:], fill=np.nan))

        # Method 2: WeightedSparse::apply()
        valA2 = AvI_x.apply(valI)

        # Compare the results
        self.assertEqual(len(valA1), valA2.shape[0])
        self.assertEqual(valA1[0].shape[0], valA2.shape[1])
        for n in range(0,nvar):
            self.assert_equal_np(valA1[n], valA2[n,:])


    def test_conserv(self):
        """Tests conservation of mass.  Checks that the amount of
        stuff (== value * weight) remains constant."""

        for fname,valI_fn in (('test_diagonal.png', self.diagonalI), ('test_elevation.png', self.elevationI)):

            valI = valI_fn()

            # A <--> I
            valAI = icebin.coo_multiply(self.AvI, valI, fill=np.nan)
            self.assert_eq_weighted(valI, self.wIvA, valAI, self.wAvI)
            valIAI = icebin.coo_multiply(self.IvA, valAI, fill=np.nan)
            self.assert_eq_weighted(valIAI, self.wIvA, valAI, self.wAvI)

            # E <--> I
            valEI = icebin.coo_multiply(self.EvI, valI, fill=np.nan)
            self.assert_eq_weighted(valI, self.wIvE, valEI, self.wEvI)

            valIEI_rough = icebin.coo_multiply(self.IvE, valEI, fill=np.nan)
            self.assert_eq_weighted(valIEI_rough, self.wIvE, valEI, self.wEvI)

            valIEI_smooth = self.IvE_smooth_x.apply(valEI)
            self.assert_eq_weighted(valIEI_smooth, self.wIvE, valEI, self.wEvI)

            # A <--> E
            valE = valEI
            valAE = icebin.coo_multiply(self.AvE, valE, fill=np.nan)
            self.assert_eq_weighted(valE, self.wEvA, valAE, self.wAvE)
            valEAE = icebin.coo_multiply(self.EvA, valAE, fill=np.nan)
            self.assert_eq_weighted(valEAE, self.wEvA, valAE, self.wAvE)

            # Plot it...
            figure = matplotlib.pyplot.figure(figsize=(22,17))

            ax = figure.add_subplot(231)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('I', val=valI, plotter=self.plotterI))

            ax = figure.add_subplot(232)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('AI', val=valAI, plotter=self.plotterA))

            ax = figure.add_subplot(233)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('IAI', val=valIAI, plotter=self.plotterI))

            ax = figure.add_subplot(234)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('IEI-rough', val=valIEI_rough, plotter=self.plotterI))

            ax = figure.add_subplot(235)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('IEI-smooth', val=valIEI_smooth, plotter=self.plotterI))

            valEAI = icebin.coo_multiply(self.EvA, valAI, fill=np.nan)
            valIEAI = icebin.coo_multiply(self.IvE, valEAI, fill=np.nan)
            ax = figure.add_subplot(236)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('IEAI', val=valIEAI, plotter=self.plotterI))

            figure.savefig(fname, dpi=100, transparent=False)



if __name__ == '__main__':
    print('BEGIN test_conerv.py')
    ice_sheet, ICEBIN_IN, ELEV_MASK = sys.argv[1:]
    sys.argv = sys.argv[:1]
    unittest.main()
