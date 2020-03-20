all : z1qx1n_bs1-onlygr.nc

# Generate grid: SeaRISE-Greenland-20km
sr_g20_searise.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating sr_g20_searise.nc: SeaRISE Greenland 20km grid (PISM-style indexing)'
	searise_grid --index_order searise

# Generate the 2 minute grid
modele_ll_g2mx2m.nc:
	modele_ll --zone g --grid 2mx2m --pole-caps=0

# Overlap two grids
modele_ll_g2mx2m-sr_g20_searise.nc: modele_ll_g2mx2m.nc sr_g20_searise.nc
	overlap modele_ll_g2mx2m.nc sr_g20_searise.nc



# Generate the ocean grid
modele_ll_g1qx1.nc:
	modele_ll --zone g --grid 1qx1 --pole-caps=0

# Overlap two grids
modele_ll_g1qx1-sr_g20_searise.nc: modele_ll_g1qx1.nc sr_g20_searise.nc
	overlap modele_ll_g1qx1.nc sr_g20_searise.nc




# ------------------------------------------------------------------

# Convert TOPO-generation input files to NetCDF, for easy viewing
Z2MX2M_NGDC = $(shell python3 ./searchenv.py Z2MX2M.NGDC MODELE_FILE_PATH)
Z2MX2M.NGDC.nc: $(Z2MX2M_NGDC)
	giss2nc $(Z2MX2M_NGDC) Z2MX2M.NGDC.nc --endian=big --names=FOCEN2,ZETOP2

Z10MX10M = $(shell python3 ./searchenv.py Z10MX10M MODELE_FILE_PATH)
Z10MX10M.nc: $(Z10MX10M)
	giss2nc $(Z10MX10M) Z10MX10M.nc --endian=big --names=FOCEANS,FLAKES,FLANDS,dZOCENs,ZONTS

ZICEHXH = $(shell python3 ./searchenv.py ZICEHXH MODELE_FILE_PATH)
ZICEHXH.nc: $(ZICEHXH)
	giss2nc $(ZICEHXH) ZICEHXH.nc --endian=big --names=dZGICH,FGICEH,ZSOLDH

ZNGDC1 = $(shell python3 ./searchenv.py ZNGDC1 MODELE_FILE_PATH)
ZNGDC1.nc: $(ZNGDC1)
	giss2nc $(ZNGDC1) ZNGDC1.nc --endian=big --names=_,_,_,FCONT1,_,FGICE1


# ------------------------------------------------------------------
# Gary's classic Fortran TOPO generator

Z :
	ln -s $HOME/modele_input/origin Z

Z1QX1N.BS1 : Z
	IC=. make_topo_f

Z1QX1N.BS1.nc : Z1QX1N.BS1
	giss2nc Z1QX1N.BS1 Z1QX1N.BS1.nc

# ------------------------------------------------------------------
# Construct TOPO file, separating out Greenland
z1qx1n_bs1-withgr.nc :
	make_topo --greenland z1qx1n_bs1-withgr.nc

z1qx1n_bs1-nogr.nc :
	make_topo z1qx1n_bs1-nogr.nc

z1qx1n_bs1-onlygr.nc : z1qx1n_bs1-withgr.nc z1qx1n_bs1-nogr.nc
	python3 make_legacy_greenland.py z1qx1n_bs1

#  ===========================================
# ETOPO1

ZETOPO1_NCEI = $(shell python3 ./searchenv.py ZETOPO1.NCEI MODELE_FILE_PATH)
ZETOPO1.NCEI.nc : $(ZETOPO1_NCEI)
	giss2nc $(ZETOPO1_NCEI) ZETOPO1.NCEI.nc --endian=big --names=FOCEAN,ZICTOP,ZSOLID --type=int16

# ---------------------------------------------
# Create gmask1m.cdl, which is checked into the Git Repo
# Create an image the user can edit
focean1m.png : ZETOPO1.NCEI.nc
	python3 etopo1_to_focean1m_png.py

# User edits focean1m.png, putting color=2 (white) over Greenland
# area.  It can cover ocean area as well, but NOT other land.
# Contains continents, plus a mask=2 over Greenland
focean1m_gmask_0.png : focean1m.png
	echo '**** User must edit focean1m.png, then save as focean1m_gmask_0.png'
	ls $@

# Contains just gridcells where mask==2, compressed
gmask1m_0.nc : focean1m_gmask_0.png
	python3 make_gmask1m_0.py

gmask1m.cdl : gmask1m_0.nc
	ncdump -l 10 gmask1m_0.nc >gmask1m.cdl
# ---------------------------------------------

gmask1m.nc : # gmask1m.cdl   This is assumed to be part of the git repo
	ncgen -o gmask1m.nc gmask1m.cdl

# Make modified ETOPO1 NetCDF file
# This also "converts" from grid-registered to pixel-registered ETOPO1
focean1m_gmask.png ZETOPO1.NCEI-SeparateGreenland.nc : ZETOPO1.NCEI.nc gmask1m.nc
	python3 regenerate_focean1_gmask.py

# ------------------------------------------------
# Generate global map of 1-minute ice, ocean mask, elevation
# This is used to generate elevation classes and ModelE TOPO files
#ZETOPO1.NCEI-SeparateGreenland.nc

# With Greenland
etopo1_ice_g1m.nc : ZETOPO1.NCEI-SeparateGreenland.nc ZNGDC1.nc
	etopo1_ice -g etopo1_ice_g

#g1qx1-etopo1_ice_g1m.nc : etopo1_ice_g1m.nc
#	overlap_hntr g1qx1 g1mx1m etopo1_ice_g1m.nc -o g1qx1-etopo1_ice_g1m.nc


# ----------------------------------------------
topoo.nc : etopo1_ice_g1m.nc Z10MX10M.nc
	make_topoo etopo1_ice_g1m.nc topoo.nc >topoo.out 2>topoo.err

# The six regridding matrices (compressed) for global ice
global_ecO.nc.mk : topoo.nc etopo1_ice_g1m.nc
	global_ec g1qx1 g1mx1m ghxh etopo1_ice_g1m.nc topoo.nc --gcm-grid ocean --matrix-names EvA -o global_ecO.nc

global_ecO.nc : global_ecO.nc.mk
	make -f global_ecO.nc.mk




# ---------------------------------------------------

topoa_nc4.nc : global_ecO.nc topoo.nc
	make_topoa -o topoa_nc4.nc --global_ecO global_ecO.nc --topoo topoo.nc

topoa.nc : topoa_nc4.nc
	nccopy -k classic topoa_nc4.nc topoa.nc

#giss2nc $DIR/Z10MX10M Z10MX10M.nc --endian=big \
#	--names=_,FLAKES
#
#giss2nc $DIR/ZICEHXH ZICEHXH.nc --endian=big \
#	--names=dZGICH,FGICEH,ZSOLDH
#
#giss2nc $DIR/ZNGDC1 ZNGDC1.nc --endian=big \
#	--names=_,_,_,FCONT1,FGICE1

# Check correctness of topoa; debugging diagnostic
topoa_check.nc : topoa.nc global_ecO.nc global_ec.nc
	python check_topoa.py


# ==================================================================
# No Greenland

# Without Greenland
etopo1_ice_ng1m.nc : ZETOPO1.NCEI-SeparateGreenland.nc ZNGDC1.nc
	etopo1_ice etopo1_ice_ng

topoo_ng.nc : etopo1_ice_ng1m.nc Z10MX10M.nc
	make_topoo etopo1_ice_ng1m.nc topoo_ng.nc >topoo_ng.out 2>topoo_ng.err


# Six regridding matrices (compressed), with mismatched regridding, w/o Greenland
global_ecO_ng.nc.mk : topoo_ng.nc etopo1_ice_ng1m.nc
	global_ec g1qx1 g1mx1m ghxh etopo1_ice_ng1m.nc topoo_ng.nc --gcm-grid ocean --matrix-names EvA -o global_ecO_ng.nc

global_ecO_ng.nc : global_ecO_ng.nc.mk
	make -f global_ecO_ng.nc.mk

#topoa_ng_nc4.nc : global_ecO_ng.nc topoo_ng.nc
#	make_topoa -o topoa_ng_nc4.nc --global_ecO global_ecO_ng.nc --topoo topoo_ng.nc
#
#topoa_ng.nc : topoa_ng_nc4.nc
#	nccopy -k classic topoa_ng_nc4.nc topoa_ng.nc

# ===========================================================================
# Merge Ice Sheet into No Greenland

# Sample PISM ice sheet
# See ../landice2/Makefile for how to generate this from original PISM state file
pismsheet_elev_mask.nc : pismsheet_elev_mask.cdl
	echo '*****************************************************************'
	echo '[makefile] Reconstituting elevation and land mask data (from PISM)'
	ncgen -o pismsheet_elev_mask.nc pismsheet_elev_mask.cdl

pismsheet_g20_icebin_in.nc : modele_ll_g1qx1-sr_g20_searise.nc pismsheet_elev_mask.nc
	echo '*****************************************************************'
	echo '[makefile] Assembling IceBin Input File from grids (contains loadable gcmO).'
	python3 write_icebin_in_base.py . modele_ll_g1qx1 sr_g20_searise pismsheet_elev_mask.nc ./pismsheet_g20_icebin_in.nc

topoo_merged.nc : pismsheet_elev_mask.nc pismsheet_g20_icebin_in.nc global_ecO_ng.nc topoo_ng.nc
	make_merged_topoo --topoo_merged topoo_merged.nc --elevmask pism:pismsheet_elev_mask.nc --gcmO pismsheet_g20_icebin_in.nc --global_ecO global_ecO_ng.nc --topoo topoo_ng.nc

topoa_merged_nc4.nc : topoo_merged.nc
	make_topoa -o topoa_merged_nc4.nc --global_ecO topoo_merged.nc --topoo topoo_merged.nc 2>err
