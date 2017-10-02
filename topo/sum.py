import netCDF4
import shutil
import numpy as np

fname1 = 'z1qx1n_bs1-nogr.nc'
fname2 = 'z1qx1n_bs1-onlygr.nc'
ofname = 'x.nc'

shutil.copyfile(fname1, ofname)

nc = netCDF4.Dataset(ofname, 'a')
nc2 = netCDF4.Dataset(fname2, 'r')

vnames = list(nc.variables.keys())
for vname in vnames:
    val = nc.variables[vname][:]
    val2 = nc2.variables[vname][:]
    mask = (np.logical_not(np.isnan(val2)))
    val[mask] = val2[mask]
    nc.variables[vname][:] = val

nc.close()
