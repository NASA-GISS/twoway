all : z1qx1n_bs1-onlygr.nc

# Generate grid: SeaRISE-Greenland-20km
sr_g20_searise.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating sr_g20_searise.nc: SeaRISE Greenland 20km grid (PISM-style indexing)'
	searise --icemodel searise

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
Z2MX2M_NGDC = $(shell ./searchenv Z2MX2M.NGDC MODELE_FILE_PATH)
Z2MX2M.NGDC.nc: $(Z2MX2M_NGDC)
	giss2nc $(Z2MX2M_NGDC) Z2MX2M.NGDC.nc --endian=big --names=FOCEN2,ZETOP2

Z10MX10M = $(shell ./searchenv Z10MX10M MODELE_FILE_PATH)
Z10MX10M.nc: $(Z10MX10M)
	giss2nc $(Z10MX10M) Z10MX10M.nc --endian=big --names=FOCEANS,FLAKES,FLANDS,dZOCENs,ZONTS

ZICEHXH = $(shell ./searchenv ZICEHXH MODELE_FILE_PATH)
ZICEHXH.nc: $(ZICEHXH)
	giss2nc $(ZICEHXH) ZICEHXH.nc --endian=big --names=dZGICH,FGICEH,ZSOLDH

ZNGDC1 = $(shell ./searchenv ZNGDC1 MODELE_FILE_PATH)
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

ZETOPO1_NCEI = $(shell ./searchenv ZETOPO1.NCEI MODELE_FILE_PATH)
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
focean1m_gmask.png ZETOPO1.NCEI-SeparateGreenland.nc : ZETOPO1.NCEI.nc gmask1m.nc
	python3 regenerate_focean1_gmask.py

# ------------------------------------------------
# Generate global map of 1-minute ice, ocean mask, elevation
# This is used to generate elevation classes and ModelE TOPO files
#ZETOPO1.NCEI-SeparateGreenland.nc

# With Greenland
etopo1_ice_g1m.nc : ZETOPO1.NCEI-SeparateGreenland.nc
	etopo1_ice -g etopo1_ice_g

g1qx1-etopo1_ice_g1m.nc : etopo1_ice_g1m.nc
	overlap_hntr g1qx1 g1mx1m etopo1_ice_g1m.nc -o g1qx1-etopo1_ice_g1m.nc


# ----------------------------------------------
topoo.nc : etopo1_ice_g1m.nc
	make_topoo topoo.nc >topoo.out 2>topoo.err

#giss2nc $DIR/Z10MX10M Z10MX10M.nc --endian=big \
#	--names=_,FLAKES
#
#giss2nc $DIR/ZICEHXH ZICEHXH.nc --endian=big \
#	--names=dZGICH,FGICEH,ZSOLDH
#
#giss2nc $DIR/ZNGDC1 ZNGDC1.nc --endian=big \
#	--names=_,_,_,FCONT1,FGICE1
