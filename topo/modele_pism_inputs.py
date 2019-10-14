# Prepares inputs for a ModelE-PISM coupled run
#
# Eg: python3 ../topo/modele_pism_inputs.py --out e17 --pism ../pism/std-greenland/g20km_10ka.nc

import sys
import argparse
import subprocess
import contextlib, os
import re
import netCDF4
import collections
import numpy as np
import icebin
import giss.ncutil
# --- Stuff from modele-control git project
import modele.gic2stieglitz
import modele.enthalpy
import ectl.pathutil

@contextlib.contextmanager
def pushd(dir):
    curdir= os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(curdir)

def make_grid(grid_cmd, grid_fname):
    """Returns True if it ran grid creation command"""
    print('***************** {}'.format(grid_fname))
    if os.path.exists(grid_fname):
        return False

    cmd = grid_cmd + ['-o', grid_fname]
    print(' '.join(cmd))
    ret = subprocess.run(cmd)
    if ret.returncode != 0:
        raise RuntimError("Command failed: {}".format(cmd))
    return True


makefile_str = """
# Recipe for generating TOPO files from PISM state files.
# This Makefile is machine-generated by modele_pism_inputs.py

all : topoa.nc

# ----------------- Things we make here
{gridA} {global_ecO_ng} {topoo_ng} :
	cd {topo_root}; $(MAKE) {gridA_leaf} {global_ecO_ng_leaf} {topoo_ng_leaf}


{gridI} : # only re-generate if it doesn't exist, it is named by content
	spec_to_grid gridI_spec.nc -o {gridI}   # gridI_spec.nc was generated from PISM state file

{exgrid} : {gridI} {gridA}
	overlap {gridA} {gridI} -o {exgrid}

# Just for kicks
gridI.nc : {gridI}
	ln -s {gridI} gridI.nc
exgridO.nc : {exgrid}
	ln -s {exgrid} exgridO.nc


gcmO.nc : {exgrid} {pism_state} {gridA} {gridI}
	echo '*****************************************************************'
	echo '[makefile] Assembling IceBin Input File from grids (contains loadable gcmO).'
	python3 {topo_root}/write_icebin_in_base.py {gridA} {gridI} {exgrid} {pism_state} ./gcmO.nc

topoo_merged.nc : {pism_state} gcmO.nc {global_ecO_ng} {topoo_ng}
	# Merge without squashing
	make_merged_topoo --squash_ec 0 --topoo_merged topoo_merged.nc --elevmask pism:{pism_state} --gcmO gcmO.nc --global_ecO {global_ecO_ng} --topoo {topoo_ng}
	# Merge with squashing
	# make_merged_topoo --topoo_merged topoo_merged.nc --elevmask pism:{pism_state} --gcmO gcmO.nc --global_ecO {global_ecO_ng} --topoo {topoo_ng}


topo_oc.nc : topoo_merged.nc
	python3 {topo_root}/make_topo_oc.py topoo_merged.nc -o topo_oc.nc

topoa_nc4.nc : topoo_merged.nc
	make_topoa -o topoa_nc4.nc --global_ecO topoo_merged.nc --topoo topoo_merged.nc 2>topoa_nc4.err

topoa.nc : topoa_nc4.nc
	nccopy -k classic topoa_nc4.nc topoa.nc
"""


# IceBin-specific rundeck extension...
icebin_cdl_str = """
// Sample Icebin parameter file.  Copy to [rundir]/config/icebin.cdl
//
// See also the following rundeck paramters to control the Stieglitz snow/firn model:
// (LISnowParams.F90`` for documentation)
//      lisnow_target_depth
//      lisnow_rho_fresh_snow
//      lisnow_rho_snow_firn_cutoff
//      lisnow_max_fract_water
//      lisnow_epsilon
//      lisnow_min_snow_thickness
//      lisnow_min_fract_cover
//      lisnow_dump_forcing
//      lisnow_percolate_nl

netcdf icebin {{
variables:
    // Setup methods (in ectl) to be run after symlinks are
    // created and before ModelE is launched.
    // Names of these attributes can be whatever you like
    int setups ;
    //    setups:landice = "ectl.xsetup.pism_landice.xsetup";

    // ModelE-specific variables cover all ice sheets
    int m.info ;

        // Definition of grids used in this ModelE run
        // (atmosphere, elevation class definitions, greenland)
        m.info:grid = "input-file:./inputs/gcmO.nc";

        // Global TOPO file, on ocean (O) grid, but missing Greenland
        m.info:topo_ocean = "input-file:./inputs/topoo_ng.nc";

        // EvO matrix, missing Greenland
        m.info:global_ec = "input-file:./inputs/global_ecO_ng.nc";

        // Where IceBin may write stuff
        m.info:output_dir = "output-dir:icebin";

        // Normally, set use_smb="t"
        // FOR TESTING ONLY: set to "f" and IceBin will pass a zero SMB and
        // appropriately zero B.C. to the ice sheet.
        m.info:use_smb = "t" ;

    // Additional variables agument m.greenland.info from main icebin_in
    // These variables are specific to Greenland
    int m.greenland.info ;
        // Output for greenland-specific stuff
        m.greenland.info:output_dir = "output-dir:greenland";

        // The ice model with which we are coupling.
        // See IceCoupler::Type [DISMAL, PISM, ISSM, WRITER]
        m.greenland.info:ice_coupler = "PISM" ;

        // Should we upate the elevation field in update_ice_sheet()?
        // Normally, yes.  But in some TEST CASES ONLY --- when the SMB
        // field was created with a different set of elevations than the
        // ice model is using --- then this can cause problems in the
        // generated SMB fields.
        // See IceModel_PISM::update_elevation
        m.greenland.info:update_elevation = "t" ;

        // Scale size of Gaussian smoother for EvI in X,Y,Z directions
        m.greenland.info:sigma = 50000., 50000., 100. ;

        // Variable currently in icebin_in, but maybe they should be moved here.
        // m.greenland.info:interp_grid = "EXCH" ;
        // m.greenland.info:interp_style = "Z_INTERP" ;
        // Also: hcdefs, indexingHC

    // Variables specific to the ModelE side of the coupling
    double m.greenland.modele ;

        // Should ModelE prepare for Dirichlet or Neumann boundary
        // conditions with the dynamic ice model?
        // See 
        m.greenland.modele:coupling_type = "DIRICHLET_BC" ;

    double m.greenland.pism ;
        // Command-line arguments provided to PISM upon initialization
        // Paths will be resolved for filenames in this list.
{greenland_pism_args}

//        m.greenland.pism:i = "input-file:pism/std-greenland/g20km_10ka.nc" ;
//        m.greenland.pism:skip = "" ;
//        m.greenland.pism:skip_max = "10" ;
//        m.greenland.pism:surface = "given" ;
//        m.greenland.pism:surface_given_file = "input-file:pism/std-greenland/pism_Greenland_5km_v1.1.nc" ;
//        m.greenland.pism:calving = "ocean_kill" ;
//        m.greenland.pism:ocean_kill_file = "input-file:pism/std-greenland/pism_Greenland_5km_v1.1.nc" ;
//        m.greenland.pism:sia_e = "3.0" ;
//        m.greenland.pism:ts_file = "output-file:greenland/ts_g20km_10ka_run2.nc" ;
//        m.greenland.pism:ts_times = "0:1:1000" ;
//        m.greenland.pism:extra_file = "output-file:greenland/ex_g20km_10ka_run2.nc" ;
//        m.greenland.pism:extra_times = "0:.1:1000" ;
//        m.greenland.pism:extra_vars = "climatic_mass_balance,ice_surface_temp,diffusivity,temppabase,tempicethk_basal,bmelt,tillwat,csurf,mask,thk,topg,usurf" ;
//        m.greenland.pism:o = "g20km_10ka_run2.nc" ;

}}
"""

def snoop_pism(pism_state):
    """Snoops around a PISM run directory, looking for key files and
    strings needed to set up IceBin.
    pism_state:
        Name of the PISM state file
    """
    # Directory of the PISM run
    pism_state = os.path.realpath(pism_state)
    pism_dir = os.path.split(pism_state)[0]

    # Read the main PISM state file
    vals = collections.OrderedDict()
    vals['pism_state'] = pism_state
    print('pism_state = {}'.format(pism_state))
    with netCDF4.Dataset(pism_state) as nc:
        # Read command line
        cmd = re.split(r'\s+', nc.command)
        config_nc = nc.variables['pism_config']
        Mx = int(getattr(config_nc, 'grid.Mx'))
        My = int(getattr(config_nc, 'grid.My'))
        vals['grid.Mx'] = Mx
        vals['grid.My'] = My

    # Parse command line into (name, value pairs)
    args = collections.OrderedDict()
    vals['args'] = args
    i = 0
    while i < len(cmd):
        if cmd[i].startswith('-'):
            if (not cmd[i+1].startswith('-')) or (len(cmd[i+1])>1 and cmd[i+1][2].isdigit()):
                args[cmd[i][1:]] = cmd[i+1]
                i += 1
            else:
                args[cmd[i][1:]] = None
        i += 1

    # Read the 'i' file for more info
    fname = os.path.normpath(os.path.join(pism_dir, args['i']))
    with netCDF4.Dataset(fname) as nc:
        vals['proj4'] = nc.proj4
        xc5 = nc.variables['x1'][:]    # Cell centers (for standard 5km grid)
        yc5 = nc.variables['y1'][:]

    # Determine cell centers on our chosen resolution
    xc = np.array(list(xc5[0] + (xc5[-1]-xc5[0]) * ix / (Mx-1) for ix in range(0,Mx)))
    yc = np.array(list(yc5[0] + (yc5[-1]-yc5[0]) * iy / (My-1) for iy in range(0,My)))
    vals['x_centers'] = xc
    vals['y_centers'] = yc
    #vals['index_order'] = (0,1)    # old PISM order; totally obsolete since 2015
    vals['index_order'] = (1,0)    # SeaRise order

    # Name grid after name of input file
    idx = int(.5 + (xc[1] - xc[0]) / 1000.)
    idy = int(.5 + (yc[1] - yc[0]) / 1000.)
    if idx == idy:
        dxdy = '{}'.format(idx)
    else:
        dxdy = '{}_{}'.format(idx,idy)

    iname = os.path.split(args['i'])[1]
    if iname.startswith('pism_Greenland'):
        vals['name'] = 'pism_g{}km_{}{}'.format(dxdy, vals['index_order'][0], vals['index_order'][1])
    else:
        vals['name'] = '{}{}km_{}'.format(os.path.splitext(iname)[0], dxdy, vals['index_order'][0], vals['index_order'][1])

    return vals

def make_pism_args(pism_dir, run_dir, pism):
    """Generates a (key, value) list of PISM arguments for the config file we will write,
    BASED ON the PISM arguments of the original bootstrap

    pism:
        Result of snoop_pism()
    """
    args = collections.OrderedDict()
    args['i'] = pism['pism_state']
    args.update((k,v) for k,v in pism['args'].items() if k != 'i')
    for arg in ('bootstrap', 'Mx', 'My', 'Mz', 'Mbz', 'z_spacing', 'Lz', 'Lbz',
        'ys', 'ye',   # Model run duration
        'extra_times', 'ts_times',
        ):
        try:
            del args[arg]
        except KeyError:
            pass


    # Get absolute name of files given in PISM command line as relative
    #for key in ('i', 'surface_given_file', 'ocean_kill_file', 'ts_file', 'extra_file', 'o'):
    for key in ('i', 'surface_given_file', 'ocean_kill_file'):
        abs = os.path.normpath(os.path.join(pism_dir, args[key]))
        args[key] = 'input-file:{}'.format(os.path.relpath(abs, run_dir))

    for key in ('ts_file', 'extra_file', 'o'):
        args[key] = 'output-file:{}'.format(os.path.join('greenland', args[key]))


    # Add to -extra_vars
    extra_vars = args['extra_vars'].split(',')
    evset = set(extra_vars)
    for var in "climatic_mass_balance,ice_surface_temp,diffusivity,temppabase,tempicethk_basal,bmelt,tillwat,csurf,mask,thk,topg,usurf".split(','):
        if var not in evset:
            extra_vars.append(var)
    args['extra_vars'] = ','.join(extra_vars)

    args['extra_times'] = '0:.1:1000'
    args['ts_times'] = '0:.1:1000'

    return args


def center_to_boundaries(xc):
    xb = np.zeros(len(xc)+1)
    xb[0] = 1.5*xc[0]-.5*xc[1]
    xb[1:-1] = (xc[0:-1] + xc[1:]) * .5
    xb[-1] = 1.5*xc[-1]-.5*xc[-2]
    return xb

def write_gridspec_xy(pism, spec_fname):
    """Given info gleaned from PISM, writes it out as a GridSpec_XY that
    can be read by the grid generator."""

    with netCDF4.Dataset(spec_fname, 'w') as nc:
        xc = pism['x_centers']
        xb = center_to_boundaries(xc)
        nc.createDimension('grid.x_boundaries.length', len(xb))
        nc_xb = nc.createVariable('grid.x_boundaries', 'd', ('grid.x_boundaries.length'))
        nc_xb[:] = xb

        yc = pism['y_centers']
        yb = center_to_boundaries(yc)
        nc.createDimension('grid.y_boundaries.length', len(yb))
        nc_yb = nc.createVariable('grid.y_boundaries', 'd', ('grid.y_boundaries.length'))
        nc_yb[:] = yb

        nc_info = nc.createVariable('grid.info', 'i', ())
        nc_info.setncattr('name', pism['name'])
        nc_info.type = 'XY'
        nc_info.indices = pism['index_order']    # Old PISM indexing order; reverse for new PISM / SeaRISE
        nc_info.sproj = pism['proj4']
        nc_info.nx = len(xc)
        nc_info.ny = len(yc)


def symlink_rel(src, dest):
    # Dereference once if this is as a link
    if os.path.islink(src):
        dir = os.path.split(src)[0]
        src_abs = os.path.abspath(os.path.normpath(os.readlink(src), dir))
    else:
        src_abs = os.path.abspath(src)
    dir = os.path.split(dest)[0]
    src_rel = os.path.relpath(src_abs, dir)
    if (os.path.islink(dest)):
        if src_rel != os.readlink(dest):
            os.symlink(src_rel, dest)
    else:
        # Not a pre-existing link, try to create it.    
        # If a file already existed there, the resulting error is appropriate.
        os.symlink(src_rel, dest)

def modele_pism_inputs(topo_root, run_dir, pism_state,
    grid_dir=None):

    """twoway_root:
        Root of the checked-out *twoway* git project / topo.  Eg: $HOME/git/twoway/topo
    run_dir:
        Name of existing ModelE run (via ectl setup) that will be annotated
    gridI_cmd:  [...]
        Command line that, when run, produces the PISM grid
        NOTE: '-o <outfile.nc>' will be appended to this command line
    gridI_leaf: (OUT)
        Name of output file in which to write the PISM grid
        (leafname only, no directory)
    grid_dir: (OUT)
        Place to look for pre-generated grids (and overlaps)

    Returns dict of:
        exgrid:
            Name of exchange grid file
    """

#    coupled_dir: (OUT)
#        Name of directory where intermediate files for coupled run
#        inputs are written.

    pism_dir = os.path.split(pism_state)[0]

    if grid_dir is None:
        grid_dir = topo_root

    os.makedirs(os.path.join(run_dir, 'inputs'), exist_ok=True)    
    symlink_rel(grid_dir, os.path.join(run_dir, 'inputs', 'grids'))
    os.makedirs(grid_dir, exist_ok=True)
#    os.makedirs(coupled_dir, exist_ok=True)

    with pushd(os.path.join(run_dir, 'inputs')):
        symlink_rel(os.path.join(topo_root, 'global_ecO_ng.nc'), 'global_ecO_ng.nc')
        symlink_rel(os.path.join(topo_root, 'topoo_ng.nc'), 'topoo_ng.nc')

    # Create ModelE grid and other general stuff (not PISM-specific)
    gridA_leaf = 'modele_ll_g1qx1.nc'
    repl = dict(    # Used to create templated makefile
        pism_state = pism_state,
        topo_root = topo_root,

        gridA = os.path.join(topo_root, gridA_leaf),
        global_ecO_ng = os.path.join(run_dir, 'inputs',  'global_ecO_ng.nc'),
        topoo_ng = os.path.join(run_dir, 'inputs', 'topoo_ng.nc'),

        gridA_leaf = gridA_leaf,
        global_ecO_ng_leaf = 'global_ecO_ng.nc',
        topoo_ng_leaf = 'topoo_ng.nc')


    # Create the PISM grid spec
    pism = snoop_pism(pism_state)
    write_gridspec_xy(pism, os.path.join(run_dir, 'inputs', 'gridI_spec.nc'))
    gridI_leaf = '{}.nc'.format(pism['name'])
#    gridI_leaf = 'sr_g20_pism.nc'
#    gridI_leaf = 'sr_g20_searise.nc'
    gridI_fname = os.path.join(grid_dir, gridI_leaf)
    repl['gridI'] = gridI_fname

    # Overlap the two
    exgrid_leaf = '{}-{}'.format(os.path.splitext(gridA_leaf)[0], gridI_leaf)
    repl['exgrid'] = os.path.join(grid_dir, exgrid_leaf)

    # Do the rest
    print('************** Makefile')

    args = make_pism_args(pism_dir, run_dir, pism)

    # ---- Generate icebin.cdl config file for IceBin
    lines = []
    for key,val in args.items():
        lines.append('        m.greenland.pism:{} = "{}" ;'.format(key,val))
    repl['greenland_pism_args'] = '\n'.join(lines)

    with open(os.path.join(run_dir, 'config', 'icebin.cdl'), 'w') as fout:
        fout.write(icebin_cdl_str.format(**repl))

    # ----- Generate TOPO file(s)
    with pushd(os.path.join(run_dir, 'inputs')):
        with open('modele_pism_inputs.mk', 'w') as fout:
            fout.write(makefile_str.format(**repl))
        cmd = ['make', '-f', 'modele_pism_inputs.mk', 'topoa.nc', 'topo_oc.nc']
        print(' '.join(cmd))
        rcmd = subprocess.run(cmd)
        if rcmd.returncode != 0:
            raise RuntimeError('Problem running the makefile')

def is_stieglitz(gic):
    """Determines if a GIC file is Lynch-Stieglitz format."""
    with netCDF4.Dataset(gic, 'r') as nc:
        return 'wsn' in nc.variables

def merge_GIC(GIC0, TOPO, pism_ic, mm, oGIC):

    """Re-generates the state of the Stieglitz model, based on the current
    state of the PISM ice sheet.  Original GIC file respects the extent of
    the ice sheet, but not the state of its surface.

    GIC0:
        Name of Stieglitz-format GIC file based on
        based on ModelE's ice sheets (i.e. no PISM coupling)
    pism_ic:
        Name of PISM initial condition file
    mm:
        Loaded-up IceBin GCMRegridder (eg: mm = icebin.GCMRegridder(icebin_in))
    """


    # -------- Load original Stieglitz state
    with netCDF4.Dataset(GIC0, 'r') as nc:
        nhc_gcm = len(nc.dimensions['nhc'])
        jm = len(nc.dimensions['jm'])
        im = len(nc.dimensions['im'])
        nlice = len(nc.dimensions['nlice'])

        if nhc_gcm > 1:
            dz = nc.variables['dz'][:,:,:,:]
            wsn = nc.variables['wsn'][:,:,:,:]
            hsn = nc.variables['hsn'][:,:,:,:]
        else:
            # Read a proper NHC from the EC-enabled TOPO File
            with netCDF4.Dataset(TOPO, 'r') as nc2:
                nhc_gcm = len(nc2.dimensions['nhc'])

            shapeEx = (nhc_gcm,jm,im,nlice)    # Ex = Stieglitz model dimensions w/ nhc_gcm
            dz = np.zeros(shapeEx)
            wsn = np.zeros(shapeEx)
            hsn = np.zeros(shapeEx)
            for ihc in range(0,nhc_gcm):
                dz[ihc,:,:,:] = nc.variables['dz'][0,:,:,:]
                wsn[ihc,:,:,:] = nc.variables['wsn'][0,:,:,:]
                hsn[ihc,:,:,:] = nc.variables['hsn'][0,:,:,:]
    nhc_ice = nhc_gcm - 1
    senth = hsn / wsn
                
    # ---------- Read masking info
    with netCDF4.Dataset(TOPO) as nc:
        fhc = nc.variables['fhc'][:]

    # --------------- Set up regridding matrices
    # Read elevmaskI
    emI_land, emI_ice = icebin.read_elevmask('pism:'+pism_ic)

    # Get regridding matrices
    nhc_localice = mm.nhc   # Elevation classes in local ice, not including global ice

    rm = mm.regrid_matrices('greenland', emI_ice, correctA=False)
    EvI_n = rm.matrix('EvI')    # No projection correction; use for regridding [J kg-1]
    rm = mm.regrid_matrices('greenland', emI_ice, correctA=True)
    AvI = rm.matrix('AvI')

    xx = AvI.to_coo()
    print('AvI has NaN', np.count_nonzero(np.isnan(xx.data)))
    xx = EvI_n.to_coo()
    print('EvI has NaN', np.count_nonzero(np.isnan(xx.data)))
    #print(xx.data)
    #print(xx.row)
    





    # ---------- Read and regrid data from PISM initial conditions
    with netCDF4.Dataset(pism_ic) as nc:
        tempI = nc.variables['effective_ice_surface_temp'][-1,:,:].reshape(-1)    # (y,x)  [K]
        fracI = nc.variables['effective_ice_surface_liquid_water_fraction'][-1,:,:].reshape(-1)    # [1]
    senthI = modele.enthalpy.temp_to_senth(tempI-273.15, fracI)    # Convert to specific enthalpy (ModelE base)
    senthE = EvI_n.apply_M(senthI).reshape((nhc_localice,jm,im))
#    senthE = (EvI_n.to_coo() * senthI).reshape((nhc_localice,jm,im))
    senthA = AvI.apply_M(senthI).reshape((jm,im))
#    print('senthI has NaN',np.count_nonzero(np.isnan(senthI)))
#    print('senthE has NaN ',np.count_nonzero(np.isnan(senthE)), senthE.shape)
#    print('senthI has ',np.count_nonzero(~np.isnan(senthI)))
#    print('senthE has ',np.count_nonzero(senthE))
#    print('senthA has ',np.count_nonzero(~np.isnan(senthA)))

    # -------------- Mask out unused ECs

    # --------------- Copy into 

    # --- EC segments
    for ihc in range(0,nhc_localice):
        senthE_ihc = senthE[ihc,:,:]
        xmask_fhc = (fhc[ihc,:,:] == 0)
        mask = np.logical_not(np.isnan(senthE_ihc))

        for il in range(0,nlice):
            senth_ihc = senth[ihc,:,:,il]
            senth_ihc[mask] = senthE_ihc[mask]
            senth_ihc[xmask_fhc] = np.nan
#            senth[ihc,:,:,il] = senth_ihc

    # ------------------------ Sea/Land
    for il in range(0,nlice):
        mask = np.logical_not(np.isnan(senthA))
        senth_ihc = senth[nhc_ice,:,:,il]
        senth_ihc[mask] = senthA[mask]


    # --------- Convert back to ModelE variables
    tsn,isn = modele.enthalpy.senth_to_temp(senth)
    hsn = senth * wsn

    with netCDF4.Dataset(GIC0, 'r') as ncin:
        with netCDF4.Dataset(oGIC, 'w', format='NETCDF3_CLASSIC') as ncout:
            # Copy GIC0 --> oGIC except for the variables we want to rewrite
            nco = giss.ncutil.copy_nc(ncin, ncout)
            nco.define_vars([x for x in ncin.variables.keys() if x not in {'dz','wsn','hsn','tsn'}])

            ncout.createDimension('nlice', nlice)
            ncout.createDimension('nhc', nhc_gcm)

            args = ('d', ('nhc', 'jm', 'im', 'nlice'))
            kwargs = {}
            dz_v = ncout.createVariable('dz', *args, **kwargs)
            wsn_v = ncout.createVariable('wsn', *args, **kwargs)
            hsn_v = ncout.createVariable('hsn', *args, **kwargs)
            tsn_v = ncout.createVariable('tsn', *args, **kwargs)
            nco.copy_data()

            # Rewrite...
            dz_v[:] = dz[:]
            wsn_v[:] = wsn[:]
            hsn_v[:] = hsn[:]
            tsn_v[:] = tsn[:]

def modele_pism_gic(run_dir, pism_state, GIC0):

    print('BEGIN modele_pism_gic')

    # ======== Step 1: Convert original GIC file to Lynch-Stieglitz GIC file

#    # Retrieve the original rundeck-provided GIC file,
#    GIC0 = os.readlink(os.path.join(run_dir, 'GIC'))
#    GIC0ns = os.path.join(run_dir, 'GIC_liclassic')
#    if is_stieglitz(GIC0):
#        GIC0 = os.readlink(GIC0ns)
#    else:
#        symlink_rel(GIC0, GIC0ns)

    stem = os.path.splitext(os.path.split(GIC0)[1])[0]
    GIC1 = os.path.join(run_dir, 'inputs', stem+'_stieglitz.nc')


    print('stem {}'.format(stem))
    print('GIC0 {}'.format(GIC0))
    print('GIC1 {}'.format(GIC1))

    modele.gic2stieglitz.gic2stieglitz(GIC0, GIC1)

    # ======== Step 2: Merge ice sheet into GIC file
    GIC2 = os.path.join(run_dir, 'inputs', stem+'_merged.nc')

    print('***** GICs')
    print(GIC0)
    print(GIC1)
    print(GIC2)


    # Obtain IceBin regridder for Atmosphere (not ocean), based on results
    # of above makefile
    mmO = icebin.GCMRegridder(os.path.join(run_dir, 'inputs', 'gcmO.nc'))
    with netCDF4.Dataset(os.path.join(run_dir, 'inputs', 'topoo_merged.nc')) as nc:
        foceanAOp = nc.variables['FOCEANF'][:]
        foceanAOm = nc.variables['FOCEAN'][:]
    mmA = mmO.to_modele((foceanAOp, foceanAOm))

    # Merge thet GIC file
    merge_GIC(
        GIC1, os.path.join(run_dir, 'inputs', 'topoa.nc'),
        pism_state, mmA, GIC2)

    # Symlink the GIC file
    with pushd(os.path.join(run_dir, 'inputs')):
        symlink_rel(GIC2, 'GIC')


def main():
    topo_root = os.path.split(os.path.realpath(__file__))[0]

    parser = argparse.ArgumentParser(description='Set up input files for a Coupled ModelE - PISM run')

    parser.add_argument('--pism', dest='pism',
        required=True,
        help='PISM state file (eg after spinup)')
    parser.add_argument('--grids', dest='grid_dir',
        default=topo_root,
        help="Name of directory for temporary reusable grid files.")
    parser.add_argument('--gic', dest='gic',
        required=True,
        help="Name of stock GIC file (no ECs, non-Stieglitz snow/firn model)")
    parser.add_argument('--run', dest='run_dir',
        required=True,
        help="Name of ModelE run, already created by `ectl setup`")
    args = parser.parse_args()

    pism = snoop_pism(args.pism)
    write_gridspec_xy(pism, 'x.nc')

    for k,v in pism['args'].items():
        if k != 'args':
            print(k,v)

    run_dir = os.path.realpath(args.run_dir)
    pism_state = os.path.realpath(args.pism)
    modele_pism_inputs(
        topo_root, run_dir, pism_state,
        grid_dir=os.path.realpath(args.grid_dir))

    GIC0 = ectl.pathutil.search_file(args.gic, os.environ['MODELE_FILE_PATH'].split(os.pathsep))
    modele_pism_gic(run_dir, pism_state, GIC0)

main()







## ===================================
#
#
#from giss import ncutil
#from modele import enthalpy
#import netCDF4
#import os
#import icebin
#from modele.constants import SHW,SHI,LHM,RHOI
#import numpy as np
#import giss
#import shutil
#
#def redo_GIC(GIC0, TOPO, pism_ic, icebin_in, GIC=None):
#
#    """Re-generates the state of the Stieglitz model, based on the current
#    state of the PISM ice sheet.  Original GIC file respects the extent of
#    the ice sheet, but not the state of its surface.
#
#    GIC0:
#        Name of GIC file that was generated (via add_fhc.py)
#        based on ModelE's ice sheet (i.e. no PISM coupling)
#    pism_ic:
#        Name of PISM initial condition file
#    icebin_in:
#        Name of IceBin config / grid description file.
#    """
#
#    # Get regridding matrices
#    mm = icebin.GCMRegridder(icebin_in)
#    rm = mm.regrid_matrices('greenland')
#    EvI_n = rm.matrix('EvI', correctA=False)    # No projection correction; use for regridding [J kg-1]
#    AvI = rm.matrix('AvI')
#
#
#    # Read info on EC segments from the TOPO file
#    with netCDF4.Dataset(TOPO) as nc:
#        segment_names = nc.variables['segments'].names.split(',')
#        x = nc.variables['segments'].bases
#        segment_bases = nc.variables['segments'].bases
#        nhc_gcm = len(nc.dimensions['nhc'])
#
#        segments = dict([(segment_names[i], (segment_bases[i], segment_bases[i+1])) for i in range(0,len(segment_names))])
#        jm = len(nc.dimensions['lat'])
#        im = len(nc.dimensions['lon'])
#
#        fhc = nc.variables['fhc'][:]
#
#    nlice = 4
#
#    # Read original ModelE initial conditions
#    with netCDF4.Dataset(GIC0, 'r') as nc:
#        wsn0A = nc.variables['wsn'][0,:,:,0]
#        hsn0A = nc.variables['hsn'][0,:,:,0]
#        senth0A = hsn0A / wsn0A
#
#    # Read data from PISM initial conditions
#    with netCDF4.Dataset(pism_ic) as nc:
#        tempI = nc.variables['effective_ice_surface_temp'][-1,:,:].reshape(-1)    # (y,x)  [K]
#        fracI = nc.variables['effective_ice_surface_liquid_water_fraction'][-1,:,:].reshape(-1)    # [1]
#    senthI = enthalpy.temp_to_senth(tempI-273.15, fracI)    # Convert to specific enthalpy (ModelE base)
#    senthA = AvI.apply(senthI).reshape((jm,im))
#    # Combine with global initial condition
#    # This merging of ice sheets can/will create a few grid cells that
#    # had an ice sheet before under ModelE, and are now off the PISM
#    # ice sheet; they've become non-ice-sheet "legacy ice."
#    # More careful (manual) merging would solve this.
#    nans = np.isnan(senthA)
#    senthA[nans] = senth0A[nans]
#
#    shapeA = (jm,im)
#    shapeEx = (nhc_gcm,jm,im,nlice)    # Ex = Stieglitz model dimensions w/ nhc_gcm
#
#    dz = np.zeros(shapeEx)    # (nhc_gcm, j, i, nlice)
#    #wsn = np.zeros(shapeEx)
#    #hsn = np.zeros(shapeEx)
#    #tsn = np.zeros(shapeEx)
#    shsn = np.zeros(shapeEx)    # Specific enthalpy
#
#    # Thickness of each layer of snow [m]
#    dz[:,:,:,0] = .1
#    dz[:,:,:,1] = 2.9
#    dz[:,:,:,2] = 3.
#    dz[:,:,:,3] = 4.
#
#    # Initialize everything at ice density (promotes stability vs. ice sheet below)
#    wsn = dz * RHOI
#
#    # Initialize everything at 1/2 ice density (this IS the surface...)
#    # wsn = dz * RHOI * .5
#
#    # ------------------------ Legacy Segment
#    base,end = segments['legacy']
#    for il in range(0,nlice):
#        shsn[base,:,:,il] = senthA
#
#    # ------------------------ Sea/Land
#    base,end = segments['sealand']
#    for ihc in range(base,end):
#        for il in range(0,nlice):
#            shsn[ihc,:,:,il] = senthA
#
#    # ------------------------ EC segments
#    base,end = segments['ec']
#    nhc = end-base
#    senthE = EvI_n.apply(senthI).reshape((nhc,jm,im))
#    for ihc in range(0,nhc):
#        senthE_ihc = senthE[ihc,:,:]
#        nans = np.isnan(senthE_ihc)
#        senthE_ihc[nans] = senthA[nans]
#
#    for il in range(0,nlice):
#        shsn[base:end,:,:,il] = senthE
#    # ----------------------------------------------
#
#    shsn[fhc == 0] = np.nan
#
#    tsn,isn = enthalpy.senth_to_temp(shsn)
#    hsn = shsn * wsn
#
#    with netCDF4.Dataset(GIC, 'w') as ncout:
#        with netCDF4.Dataset(GIC0, 'r') as ncin:
#            # Copy GIC0 --> GIC except for the variables we want to rewrite
#            nco = giss.ncutil.copy_nc(ncin, ncout,
#                var_filter = lambda x : None if x in {'dz', 'wsn', 'hsn', 'tsn'} else x)
#            nco.define_vars(zlib=True)
#            ncout.createDimension('nlice', 4)
#            ncout.createDimension('nhc', nhc_gcm)
#
#            args = 'd', ('nhc', 'jm', 'im', 'nlice')
#            kwargs = {'zlib' : True}
#            dz_v = ncout.createVariable('dz', *args, **kwargs)
#            wsn_v = ncout.createVariable('wsn', *args, **kwargs)
#            hsn_v = ncout.createVariable('hsn', *args, **kwargs)
#            tsn_v = ncout.createVariable('tsn', *args, **kwargs)
#            nco.copy_data()
#
#            # Rewrite...
#            dz_v[:] = dz[:]
#            wsn_v[:] = wsn[:]
#            hsn_v[:] = hsn[:]
#            tsn_v[:] = tsn[:]
#
#
#def xsetup(args_run, rd):
#    """args_run:
#        Main run directory
#    rd:
#        The rundeck, parsed and loaded."""
#
#    GIC0 = rd.params.files['GIC0'].rval
#    TOPO = rd.params.files['TOPO'].rval
#
#    with netCDF4.Dataset(os.path.join('config', 'icebin.nc')) as nc:
#        pism_ic = nc.variables['m.greenland.pism'].i
#        icebin_in = nc.variables['m.info'].grid
#
#    redo_GIC(GIC0, TOPO, pism_ic, icebin_in, GIC=os.path.join(args_run, 'GIC'))
#
#
