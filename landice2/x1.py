import netCDF4

#fname = 'pismsheet_g20_icebin_in.nc'
#prefix = 'm.greenland.'

fname = 'modele_ll_g2x2_5-sr_g20_pism.nc'
prefix = ''


nc = netCDF4.Dataset(fname)
native_area = nc.variables[prefix+'exgrid.cells.native_area'][:]

print(native_area[9950])

vertices_xy = nc.variables[prefix+'exgrid.vertices.xy'][:]
for iV in (12320, 12322, 12319):
    print('Vertex', iV, vertices_xy[iV,:])

