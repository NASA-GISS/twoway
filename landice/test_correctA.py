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

ice_sheet = 'greenland'
ICEBIN_IN = 'icebin_in.nc'

regrid_names = ('IvA', 'AvI', 'IvE', 'EvI', 'EvA', 'AvE')

class CorrectATests(unittest.TestCase):
    """Tests the correctA flag of GCMRegridder is working properly."""

    def setUp(self):
        self.mm = icebin.GCMRegridder(ICEBIN_IN)
        self.rm = self.mm.regrid_matrices(ice_sheet)
        with netCDF4.Dataset(ICEBIN_IN) as nc:
            self.indexingA = ibgrid.Indexing(nc, 'm.gridA.indexing')
            self.indexingHP = ibgrid.Indexing(nc, 'm.indexingHP')
            self.indexingI = ibgrid.Indexing(nc, 'm.{}.gridI.indexing'.format(ice_sheet))
            self.plotterI = ibplotter.read_nc(nc, 'm.{}.gridI'.format(ice_sheet))
            self.plotterA = ibplotter.read_nc(nc, 'm.gridA')

#        self.elevI, self.maskI = giss.pism.read_elevI_maskI('elev_mask.nc')

#        self.AvI,self.wAvI = self.rm.regrid('AvI', scale=True, correctA=False)
#        self.IvA,self.wIvA = self.rm.regrid('IvA', scale=True, correctA=False)
#        self.EvI,self.wEvI = self.rm.regrid('EvI', scale=True, correctA=False)
#        self.IvE,self.wIvE = self.rm.regrid('IvE', scale=True, correctA=False)
#        self.EvA,self.wEvA = self.rm.regrid('EvA', scale=True, correctA=False)
#        self.AvE,self.wAvE = self.rm.regrid('AvE', scale=True, correctA=False)


#        self.nA = self.AvI.shape[0]
#        self.nE = self.EvI.shape[0]

#        print('nA', self.nA)
#        print('nE', self.nE)

    # -----------------------------------------------------
    def test_correctA(self):
        """Tests conservation of mass.  Checks that the amount of
        stuff (== value * weight) remains constant."""



        fname = 'test_correctA.png'
        figure = matplotlib.pyplot.figure(figsize=(22,17))

        for i,(correctA,msg) in enumerate(((False, 'should see constant=1'), (True, 'should see rainbow stripes'))):
            IvE,wIvE = self.rm.regrid('IvE', scale=True, correctA=correctA)
            nE = IvE.shape[1]

            valE = (np.zeros((nE,)) + 1).reshape(-1)


            # E <--> I
            valIE = icebin.coo_multiply(IvE, valE, fill=np.nan)

            # Plot it...
            ax = figure.add_subplot(1,2,i+1)
            basemap = giss.basemap.greenland_laea(ax=ax)
            giss.plot.plot_var(ax=ax, basemap=basemap,
                **deprecated_plot_params.plot_params('IE-{}\n({})'.format(
                'corrected' if correctA else 'uncorrected', msg),
                val=valIE, plotter=self.plotterI))

        figure.savefig(fname, dpi=100, transparent=False)



if __name__ == '__main__':
    unittest.main()
