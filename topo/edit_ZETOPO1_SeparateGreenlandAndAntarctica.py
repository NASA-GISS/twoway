import xarray as xr

ds_g = xr.open_dataset('ZETOPO1.NCEI-SeparateGreenland.nc')
ds_g['FLAND'] = 3. - ds_g.FOCEAN
mask = (ds_g.FLAND).where(xr.ufuncs.logical_and(ds_g.jm1m<1700,ds_g.FLAND>0.))
mask = mask.where(mask==3)

# When True, return values from x, otherwise returns values from y
ds_g['FOCEAN'] = (ds_g.FOCEAN).where(mask!=mask, ds_g.FLAND)

ds_g.to_netcdf('ZETOPO1.NCEI-SeparateGreenlandAndAntarctica.nc')
