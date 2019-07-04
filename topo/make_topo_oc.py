import os
import sys
import netCDF4
import argparse

"""Copies select variables out of a merged TOPOO file, to create a
TOPO_OC file ready for use in ModelE wit interactive ocean."""


#ncdump -h OZ144X90N_nocasp.1.nc
#netcdf OZ144X90N_nocasp.1 {
#dimensions:
#        lono = 144 ;
#        lato = 90 ;
#variables:
#        float lono(lono) ;
#                lono:units = "degrees_east" ;
#        float lato(lato) ;
#                lato:units = "degrees_north" ;
#        float focean(lato, lono) ;
#        float zatmo(lato, lono) ;
#        float zocean(lato, lono) ;
#}

# ------------------------------------------------------------
parser = argparse.ArgumentParser(description='Create topo_oc.nc file in NetCDF3 format required by ModelE')

parser.add_argument('topoo',
    help="Name of merged TOPOO file")
parser.add_argument('-o', dest='ofname',
    help="Name of output TOPO_OC file")

args = parser.parse_args()
# ------------------------------------------------------------

def copy_var(vsrc, vdest):
    """Copies value and attributes from one NetCDF variable to another"""
    for aname in vsrc.ncattrs():
        setattr(vdest, aname, getattr(vsrc, aname))

    vdest[:] = vsrc[:]


with netCDF4.Dataset(args.topoo, 'r') as ncin:
    with netCDF4.Dataset(args.ofname, 'w', format='NETCDF3_CLASSIC') as ncout:

        # Create the variables
        ncout.createDimension('lono', len(ncin.dimensions['im']))
        lono = ncout.createVariable('lono', 'd', ('lono',))
        lono[:] = ncin.variables['lon'][:]

        ncout.createDimension('lato', len(ncin.dimensions['jm']))
        lato = ncout.createVariable('lato', 'd', ('lato',))
        lato[:] = ncin.variables['lat'][:]

        copy_var(ncin.variables['FOCEAN'],
            ncout.createVariable('focean', 'd', ('lato', 'lono')))

        copy_var(ncin.variables['ZATMO'],
            ncout.createVariable('zatmo', 'd', ('lato', 'lono')))

        copy_var(ncin.variables['ZOCEAN'],
            ncout.createVariable('zocean', 'd', ('lato', 'lono')))
