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


parser = argparse.ArgumentParser(description='Produce elevation-classified input files')
parser.add_argument('--topo-leaf', dest='topo',
    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
parser.add_argument('--gic-leaf', dest='gic',
    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
parser.add_argument('--icebin-in', dest='icebin_in',
    help="Name of IceBin input file")
parser.add_argument('--elev-mask', dest='elev_mask',
    help="name of elevation / mask file from the high-res ice sheet (extract of a PISM file).")
parser.add_argument('--elev-mask-type', dest='elev_mask_type',
    help="File type for elev-mask: pism, mar")
parser.add_argument('--stieglitz', action='store_true', default=False,
    help="Set to generate initial conditions for Stieglitz model")

args = parser.parse_args()

# This script needs to:
# 1. Load up IceBin and create the matrix AvE
#
# 2. Write new TOPO file based on hi-res ice sheet
#
# 3. Write new GIC file:
#    a) FHC derived from AvE (plus legacy HC)
#    b) nhc dimension added to various variables

# -------- GCM Input Files
#TOPO_leaf = 'Z2HX2fromZ1QX1N'
#GIC_leaf = 'GIC.144X90.DEC01.1.ext_1'

# -------- Input Files made by us
#ICEBIN_IN = './pismsheet_g20_icebin_in.nc'
#ELEV_MASK = './pismsheet_elev_mask.nc'

# --------------------------------------
# ------- Find Input Files
file_path = os.environ['MODELE_FILE_PATH'].split(os.pathsep)
iTOPO = giutil.search_file(args.topo+'.nc', file_path)
print(' READ: iTOPO = {}'.format(iTOPO))
iGIC = giutil.search_file(args.gic+'.nc', file_path)
print(' READ:  iGIC = {}'.format(iGIC))


# -------- New Output Files
#odir = os.path.join(os.environ['HOME'], 'modele_input', 'local', 'landice')
odir = '.'
oTOPO = os.path.join(odir, args.topo+'_EC2-{segment}.nc')
oGIC = os.path.join(odir, args.gic+'_EC2.nc')
print('WRITE: oTOPO = {}'.format(oTOPO))
print('WRITE:  oGIC = {}'.format(oGIC))

# --------------------------------
# 1. Load up IceBin and create the matrix AvE
mm = icebin.GCMRegridder(args.icebin_in)
rm = mm.regrid_matrices('greenland')
wAvE,AvE,_ = rm.matrix('AvE', scale=True)()
wEvI,EvI,_ = rm.matrix('EvI', scale=True)()
wAvI,AvI,_ = rm.matrix('AvI', scale=True)()

with netCDF4.Dataset(args.icebin_in) as nc:
    indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
    hcdefs_ice = nc.variables['m.hcdefs'][:]
    nhc_ice = len(nc.dimensions['m.nhc'])
    indexA_sub = nc.variables['m.gridA.cells.index'][:]
    areaA_sub = nc.variables['m.gridA.cells.native_area'][:]
    nA1 = getattr(nc.variables['m.gridA.info'], 'cells.nfull')

areaA1 = np.zeros((nA1,))
areaA1[indexA_sub] = areaA_sub    # Native area of full grid cell (on sphere)


# ----------------------------------
# 2. Compute new land surface fractions based on hi-res ice sheet
if args.elev_mask_type == 'pism':
    with netCDF4.Dataset(args.elev_mask) as nc:
        thk = nc.variables['thk'][:]
        topg = nc.variables['topg'][:]
    elevI = topg + thk
    elevEice1 = icebin.coo_multiply(EvI, elevI)
    elevA1 = icebin.coo_multiply(AvE, elevEice1)

elif args.elev_mask_type == 'mar':
    with netCDF4.Dataset(args.elev_mask) as nc:
        thk = nc.variables['thk'][0,:,:]
        topg = nc.variables['topg'][0,:,:] #Had to add zeros to MAR to get into right
                                           #format.. must subset array here.
        thk = thk[:]
        topg = topg[:]

    elevI = topg + thk #All topography. Ocean elevation in the file must be negative, 
                       #to produce NaN values for averaging in ocean grid boxes.
    elallI = elevI  #Topography including ice, land, sea.
    elallI[elallI<0.0] = 0.0  #Sea level is set to 0.

    elevEice1 = icebin.coo_multiply(EvI, elevI)
    elevA1 = icebin.coo_multiply(AvE, elevEice1)
    elallA1 = icebin.coo_multiply(AvI, elallI)

else:
    raise ValueError('Illegal elev-mask-type: {}'.format(args.elev_mask_type))


with netCDF4.Dataset(iTOPO) as ncin:
    focean = ncin.variables['focean'][:]
    flake = ncin.variables['flake'][:]
    fgrnd = ncin.variables['fgrnd'][:]    # Alt: FEARTH0
    fgice = ncin.variables['fgice'][:]    # Alt: FLICE
    zatmo_m = ncin.variables['zatmo'][:]    # _m means [meters]

shapeA = zatmo_m.shape
elevA = elevA1.reshape(shapeA)
areaA = areaA1.reshape(shapeA)
wA = wAvE.reshape(shapeA)
_maskA = ~np.isnan(elevA)
if args.elev_mask_type == 'mar':
    elallA = elallA1.reshape(shapeA)

# ------ Adjust land type fractions
fgice0 = copy.copy(fgice)
fgice[_maskA] = wA[_maskA] / areaA[_maskA]
fgrnd = 1. - (flake + focean + fgice)
fgrnd[fgrnd<0] = 0.
focean = 1. - (flake + fgrnd + fgice)
if not np.all(focean >= 0):
    print('focean', focean[focean<0])
    raise ValueError('FOCEAN went negative; take from some other land surface type')

# ---------------------------------------------------
# 3a) Derive FHC from AvE (plus legacy HC)
#     (Other than the locality check, this should be just FHC == wE)

# ------- Set up elevation class structure
segments = list()

# Segment 0: The legacy elevation class
legacy_base = 0
nlegacy = 1
segments.append(('legacy', legacy_base))

# Segment 1: Two elevation classes only: one for sea, one for land
sealand_base = legacy_base + nlegacy
nsealand = 2
segments.append(('sealand', sealand_base))

# Segment 2: Full elevation classes
ec_base = sealand_base + nsealand
segments.append(('ec', ec_base))

# Total number of EC's across all segments
nhc_gcm = ec_base + nhc_ice

# -- Initialize per-EC arrays
shapeE_gcm = (nhc_gcm, shapeA[0], shapeA[1])
fhc = np.zeros(shapeE_gcm)
underice = np.zeros(shapeE_gcm, dtype=np.int8)
elevE = np.zeros(shapeE_gcm)


# ------- Segment 0: Legacy Segment
# Compute the legacy elevation class, but don't include in sums
fhc[legacy_base,fgice != 0] = 1.   # Legacy ice for Greenland and Antarctica
underice[legacy_base,fgice != 0] = UI_NOTHING

#TODO: This is circular.  zatmo_m has not been set yet!!!

elevE[legacy_base,:,:] = zatmo_m
if args.elev_mask_type == 'pism':
    # Assume elevation=0 for non-ice-sheet areas.  This is OK for ocean portions,
    # not OK for bare land portions.
    elevE[legacy_base,_maskA] = elevA[_maskA] * fgice[_maskA]
elif args.elev_mask_type == 'mar':
    # Use average elevation including land, ocean, ice from high res. grid.
    elevE[legacy_base,_maskA] = elallA[_maskA]


# ------- Segment 1: SeaLand Segment
# ihc=0: Non-ice portion of grid cell at sea level

# FHC is fraction of ICE-COVERED area in this elevation class
# Therefore, FHC=0 for the sea portion of the SeaLand Segment
# NOT: fhc[sealand_base,_maskA] = 1.-fgice[_maskA]
# We could do away with this EC altogether because it's not used.
fhc[sealand_base,_maskA] = 0.
underice[sealand_base,_maskA] = 0
elevE[sealand_base,_maskA] = 0.
# ihc=1: Ice portion of grid cell at mean for the ice portion
# FHC is fraction of ICE-COVERED area in this elevation class
# Therefore, FHC=1 for the land portion of the SeaLand Segment
# NOT: fhc[sealand_base+1,_maskA] = fgice[_maskA]
fhc[sealand_base+1,_maskA] = 1.
underice[sealand_base+1,_maskA] = UI_NOTHING
elevE[sealand_base+1,_maskA] = elevA[_maskA]


# ---------- Segment 2: Full Elevation Classes
shapeE = (nhc_ice, shapeA[0], shapeA[1])
shapeE2 = (nhc_ice, shapeA[0] * shapeA[1])
shapeE2_gcm = (nhc_gcm, shapeA[0] * shapeA[1])
fhcE2 = fhc.reshape(shapeE2_gcm)
undericeE2 = underice.reshape(shapeE2_gcm)

elevEice = elevEice1.reshape(shapeE)

for iA,iE,weight in zip(AvE.row, AvE.col, AvE.data):
    # iE must be contained within cell iA (local propety of matrix)
    iA2,ihc = indexingHC.index_to_tuple(iE)
    if iA2 != iA:
        raise ValueError('Matrix is non-local: iA={}, iE={}, iA2={}'.format(iA,iE,iA2))
    fhcE2[ec_base+ihc,iA] = weight
    undericeE2[ec_base+ihc,iA] = UI_ICEBIN

print('elevE', elevE.shape)
print('hcdefs_ice', hcdefs_ice.shape)
for j in range(0,elevE.shape[1]):
    for i in range(0,elevE.shape[2]):
        elevE[ec_base:,j,i] = hcdefs_ice[:]



# TODO: Height-classify other GIC variables

# -------------------------------------------------------------
# 4) Fix bottom of atmosphere

# Atmosphere sees mean of elevations over entire grid cell
zatmo_m[_maskA] = elevE[legacy_base,_maskA]


# -------------------------------------------------------------
# 5) Convert snowli/tlandi to Stieglitz state variables

with netCDF4.Dataset(iGIC) as ncin:
    snowli = ncin.variables['snowli'][:]    # snowli[nhc=1, jm, im]
    tlandi = ncin.variables['tlandi'][:]    # tlandi[nhc=1, jm, im, 2]

if args.stieglitz:
    # Generate GIC variables for the Stieglitz model
    # OUTPUT: dz,wsn,hsn,tsn

    nlice = 5    # Number of layers in ice
    shape_stieglitz = (nhc_gcm, shapeA[0], shapeA[1], nlice)
    dz = np.zeros(shape_stieglitz)
    wsn = np.zeros(shape_stieglitz)
    hsn = np.zeros(shape_stieglitz)
    tsn = np.zeros(shape_stieglitz)
    for ihc in range(0, nhc_gcm):

        # Handle the "snow" layer in the old ModelE
        wsn[ihc,:,:,0] = snowli[0,:,:]
        dz[ihc,:,:,0] = wsn[ihc,:,:,0] / RHOS

        # Set up thicknesses in the ice layers
        dz[ihc,:,:,1] = .1
        dz[ihc,:,:,2] = 2.9
        dz[ihc,:,:,3] = 3.
        dz[ihc,:,:,4] = 4. - dz[ihc,:,:,0]    # Balance volume from snow

        # Set mass of lower layers, as solid ice
        wsn[ihc,:,:,1:] = dz[ihc,:,:,1:] * RHOI

        # Set temperatures of the layers
        tsn[ihc,:,:,0] = tlandi[0,:,:,0]
        tsn[ihc,:,:,1:3] = tlandi[0,:,:,0:2]
        tsn[ihc,:,:,3] = tlandi[0,:,:,1]
        tsn[ihc,:,:,4] = tlandi[0,:,:,1]

        # Set enthalpy based on temperature
        hsn[ihc,:,:,:] = wsn[ihc,:,:,:] * (tsn[ihc,:,:,:] * SHI - LHM)

        # Eliminate snow layer if it is empty
        for j in range(0,dz.shape[1]):
    #        print(j,dz.shape[1])
            for i in range(0,dz.shape[2]):
                if dz[ihc,j,i,0] == 0.:
                    dz[ihc,j,i,0:3] = dz[ihc,j,i,1:4]
                    wsn[ihc,j,i,0:3] = wsn[ihc,j,i,1:4]
                    hsn[ihc,j,i,0:3] = hsn[ihc,j,i,1:4]
                    tsn[ihc,j,i,0:3] = tsn[ihc,j,i,1:4]

                    # Split last layer in two
                    dz[ihc,j,i,3:5] = dz[ihc,j,i,4] * .5
                    wsn[ihc,j,i,3:5] = wsn[ihc,j,i,4] * .5
                    hsn[ihc,j,i,3:5] = hsn[ihc,j,i,4] * .5
                    tsn[ihc,j,i,3:5] = tsn[ihc,j,i,4]


                # This is now done upon loading LANDICE_IC (LISnow.F90)
                ## Remove extra snow layer, which causes problems if it is too thin.
                #params = modelexe.Lisnowbase_Mod.Lisnowparams()
                #params.max_nl = nl_ice
                #params.target_nl_ice = nl_ice
                #fexec(lambda: modelexe.Lisnowbase_Mod.
                #    snow_redistr(params,
                #        dz[ihc,j,i,:],
                #        wsn[ihc,j,i,:],
                #        hsn[ihc,j,i,:],
                #        nl_ice, 0, 1.0)
                #)
else:
    # Non-Stieglitz run; generate inital condition for "old" 3m snow model.
    # OUTPUT: snowli, tlandi

    snowli0 = snowli
    tlandi0 = tlandi
    snowli = np.zeros( (nhc_gcm,) + snowli0.shape[1:] )
    tlandi = np.zeros( (nhc_gcm,) + tlandi0.shape[1:] )

    for ihc in range(0,nhc_gcm):
        snowli[ihc,:] = snowli0[:]
        tlandi[ihc,:] = tlandi0[:]


    # Fix up snowli and tlandi for places where the hi-res model
    # has ice but the original ModelE model does not.
    _newice = np.logical_and(snowli[0,:,:] == 0, fgice > 0)
    snowli[:,_newice] = 0      # No snow to start with
    tlandi[:,_newice] = -10    # degC

        

# -------------------------------------------------------------
# 6) Write the TOPO file(s)


# Set appropriate segments to diagnostic
for segment in ['legacy', 'sealand', 'ec']:

    # Set non-prognostic segments to diagnostic
    fhc_final = np.copy(fhc)
    if segment != 'legacy':
        fhc_final[legacy_base,_maskA] *= 1e-30    # Remove weight from legacy ice in Greenland
    if segment != 'sealand':
        fhc_final[sealand_base:sealand_base+nsealand,:,:] *= 1e-30
    if segment != 'ec':
        fhc_final[ec_base:nhc_gcm,:,:] *= 1e-30

    # Set diagnostic grid cells to UI_NOHING
    underice[np.logical_and(fhc_final==1e-30, underice==UI_ICEBIN)] = UI_NOTHING

    fhc_sum = sum(fhc_final, 0)

    with netCDF4.Dataset(iTOPO) as ncin:
        with netCDF4.Dataset(oTOPO.format(segment=segment), 'w', format='NETCDF3_CLASSIC') as ncout:
            # ---- Set up meta-data of files this depends on...
            files = ncout.createVariable('files', 'i')
            install_path = ncout.createVariable('install_paths', 'i')
            files.source = os.path.abspath(iTOPO)

            files.elev_mask = os.path.abspath(args.elev_mask)
            install_path.elev_mask = 'landice'

            files.icebin_in = os.path.abspath(args.icebin_in)
            install_path.icebin_in = 'landice'


            # Store segment information
            segments_v = ncout.createVariable('segments', 'i')
            segments_v.description = 'Multiple elevation class sets run at once; see init_cond/ice_cheet_ec/add_fhc.py'
            segments_v.names = ','.join([x[0] for x in segments])
            segments_v.bases = [x[1] for x in segments] + [nhc_gcm]

            # --------------------------

            ncc = copy_nc(ncin, ncout)

            ncc.createDimension('nhc', nhc_gcm)
            ncc.copyDimensions('lat', 'lon')

            # Our new varables
            ncc.createVariable('fhc', 'd', ('nhc', 'lat', 'lon'))
            ncc.createVariable('underice', 'd', ('nhc', 'lat', 'lon'))
            ncc.createVariable('elevE', 'd', ('nhc', 'lat', 'lon'))
            ncc.createVariable('fhc_sum', 'd', ('lat', 'lon')).description = \
                'Verification: Sum of fhc over each atmosphere grid cell.'

            ncc.define_vars()
            ncc.createVariable('fraction_sum', 'd', ('lat', 'lon')).description = \
                'Verification: Sum of all land fractions (fgice + fgrnd + focean + flake)'

            ncc.copy_data()

            ncout.variables['focean'][:] = focean[:]
            #ncout.variables['flake'][:] = flake[:]
            ncout.variables['fgrnd'][:] = fgrnd[:]
            ncout.variables['fgice'][:] = fgice[:]
            ncout.variables['zatmo'][:] = zatmo_m[:]
            ncout.variables['fraction_sum'][:] = (fgice + fgrnd + focean + ncout.variables['flake'][:])[:]    # Should be 1
            ncout.variables['fhc'][:] = fhc_final[:]
            ncout.variables['underice'][:] = underice[:]
            ncout.variables['elevE'][:] = elevE[:]
            ncout.variables['fhc_sum'][:] = fhc_sum[:]   # Sanity check, not used


# -------------------------------------------------------------
# 7) Write the GIC file
with netCDF4.Dataset(iGIC) as ncin:
    with netCDF4.Dataset(oGIC, 'w', format='NETCDF3_CLASSIC') as ncout:

        # ---- Store provenance in standard way...
        files = ncout.createVariable('files', 'i')
        install_path = ncout.createVariable('install_paths', 'i')
        files.source = os.path.abspath(iGIC)

# We need this only on the TOPO file
#        # This is not installed
#        files.elev_mask = os.path.abspath(args.elev_mask)
#        install_path.elev_mask = 'landice'
#        files.icebin_in = os.path.abspath(args.icebin_in)
#        install_path.icebin_in = 'landice'

        ncc = copy_nc(ncin, ncout,
            var_filter = lambda x : None if x in {'snowli', 'tlandi'} else x)

        ncc.createDimension('nhc', nhc_gcm)
        if args.stieglitz:
            ncc.createDimension('nlice', nlice)
        ncc.copyDimensions('jm', 'im')
        if not args.stieglitz:
            ncc.copyDimensions('d2')

        if args.stieglitz:
            new_ice_var = lambda name : \
                ncc.createVariable(name, 'd', ('nhc', 'jm', 'im', 'nlice'))
            new_ice_var('dz')[:] = dz[:]
            new_ice_var('wsn')[:] = wsn[:]
            new_ice_var('hsn')[:] = hsn[:]

            # tsn
            var = new_ice_var('tsn')
            var[:] = tsn[:]
            var.description = 'Temperature of layer [C].  Diagnostic only, for debugging the this input file.'

        else:

            ncc.createVariable('snowli', 'd', ('nhc', 'jm', 'im'))
            ncc.createVariable('tlandi', 'd', ('nhc', 'jm', 'im', 'd2'))
            ncout.variables['snowli'][:] = snowli[:]
            ncout.variables['tlandi'][:] = tlandi[:]

        ncc.define_vars()
        ncc.copy_data()

print(sum(sum(np.logical_and(snowli[0,:,:] == 0, fgice > 0))))
