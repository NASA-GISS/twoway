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

def main():
    ICEBIN_IN = 'pismsheet_g20_icebin_in.nc'
    mm = icebin.GCMRegridder(ICEBIN_IN)
    rm = mm.regrid_matrices('greenland')
    AvI,wAvI = rm.regrid('AvI', scale=True)

    print(AvI.shape)
    print(wAvI.shape)
    print(type(AvI))

    for i,j,v in zip(AvI.row, AvI.col, AvI.data):
        print('({}, {}) = {}'.format(i,j,v))

main()
