import xarray as xr

ds_in = xr.open_dataset('/discover/nobackup/projects/giss/prod_input_files/ZETOPO1.nc')[['EOCEAN','ZICETOP','ZSOLIDG']]

ds = ds_in.rename({'EOCEAN':'FOCEAN','ZSOLIDG':'ZSOLID','ZICETOP':'ZICTOP'})
ds = ds.rename({'IM':'im1m','JMp1':'jm1m_gridreg'})

mydata = ds.ZICTOP
mydata = mydata.where(mydata>0.,ds.ZSOLID) # add in solid ground topography for non-ice-covered regions
ds['ZICTOP'] = mydata

ds.attrs['Note2'] = 'Edited for ModelE Land Ice, 2023, L Roach'
ds.to_netcdf('ZETOPO1.NCEI.nc')
