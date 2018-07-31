import netCDF4
import ibmisc
import numpy as np

# Check basic properties of the TOPOA file.

topoa_nc = 'topoa.nc'


# Check sum of fhc in TOPOA file
with netCDF4.Dataset(topoa_nc,'r') as nc:
    fhc = nc.variables['fhc'][:]

fhc1 = sum(fhc,0)

# Check sum of fhc from AvE matrix (mismatched)
fhc_AvE_mm = np.zeros(fhc.shape[1:])
ncio = ibmisc.NcIO('global_ec_mm.nc', 'r')
lw = ibmisc.nc_read_weighted(ncio, 'AvE')
ncio.close()

AvE_mm = lw.to_coo()

for iA,iE,val in zip(AvE_mm.row, AvE_mm.col, AvE_mm.data):
    jj = iA // fhc1.shape[1]
    ii = iA - (jj * fhc1.shape[1])
    fhc_AvE_mm[jj,ii] += val

wAvE_mm = lw.get_weights(0)


# Check sum of fhc from AvE matrix (regular)
fhc_AvE = np.zeros(fhc.shape[1:])
ncio = ibmisc.NcIO('global_ec.nc', 'r')
lw = ibmisc.nc_read_weighted(ncio, 'AvE')
ncio.close()

AvE = lw.to_coo()
for iA,iE,val in zip(AvE.row, AvE.col, AvE.data):
    jj = iA // fhc1.shape[1]
    ii = iA - (jj * fhc1.shape[1])
    fhc_AvE[jj,ii] += val
wAvE = lw.get_weights(0)

r1 = wAvE / wAvE_mm
wRatio = np.zeros(wAvE_mm.shape)
wRatio[:] = wAvE
wRatio[np.logical_not(np.isinf(r1))] = np.nan

#wRatio[:] = wAvE_mm
#wRatio[wAvE != 0] = np.nan
#wRatio[wAvE_mm == 0] = np.nan

#wRatio = wAvE / wAvE_mm
#wRatio[np.isnan(wRatio)] = np.nan
#wRatio[np.logical_not(np.isinf(wRatio))] = 0
#wRatio[np.isinf(wRatio)] = 17
# Check weights


with netCDF4.Dataset('topoa_check.nc','w') as nc:
    nc.createDimension('jm', fhc1.shape[0])
    nc.createDimension('im', fhc1.shape[1])
    ncv = nc.createVariable('fhc1', 'd', ('jm','im'))
    ncv[:] = fhc1[:]
    ncv = nc.createVariable('fhc_AvE_mm', 'd', ('jm','im'))
    ncv[:] = fhc_AvE_mm[:]
    nc.createVariable('wAvE_mm', 'd', ('jm','im'))[:] = wAvE_mm

    ncv = nc.createVariable('fhc_AvE', 'd', ('jm','im'))
    ncv[:] = fhc_AvE[:]
    nc.createVariable('wAvE', 'd', ('jm','im'))[:] = wAvE
    nc.createVariable('wRatio', 'd', ('jm','im'))[:] = wRatio


print(fhc.shape)
print(fhc1.shape)
