
# Set to your Python 3 command.  Should not need to be set if an
# appropriate Python3 environment module is already loaded.
PYTHON3 = python3

# Set this to the directory where your PISM spinup file resides.
# (NOT necessary to run the tests in this directory)
#PISM_SPINUP_DIR = /home2/rpfische/exp/151014-integrate/build/std-greenland
PISM_SPINUP_DIR = ../pism/std-greenland

# --------------------------------------------------------------

# Run the main test.
all: test_diagonal.png test_elevation.png sr_g20_searise.pdf modele_ll_g1qx1.pdf modele_ll_g1qx1-sr_g20_searise.pdf matrices.pik GIC.144X90.DEC01.1.ext_1-fhc.nc Z1QX1fromZ1QX1N-fhc.nc

clean:
	rm *.nc *.pdf *.png

# =========== Generate stuff we check into git
# This requires external software (PISM), and should not normally need
# to be run.

# Files that will be checked into git
git_files : pismsheet_elev_mask.cdl

.INTERMEDIATE : _pismsheet_elev_mask.nc

# Extract topg, thk and mass from a PISM state file.
_pismsheet_elev_mask.nc :
	$(PYTHON3) write_elev_mask.py $(PISM_SPINUP_DIR)/g20km_10ka.nc _pismsheet_elev_mask.nc

# Convert netCDF to text-based format
pismsheet_elev_mask.cdl : _pismsheet_elev_mask.nc
	ncdump -l 10 _pismsheet_elev_mask.nc >pismsheet_elev_mask.cdl

# ================ Generate input files for the example, from text antecedents

# Reconstitute topg, thk and mass
pismsheet_elev_mask.nc : pismsheet_elev_mask.cdl
	echo '*****************************************************************'
	echo '[makefile] Reconstituting elevation and land mask data (from PISM)'
	ncgen -o pismsheet_elev_mask.nc pismsheet_elev_mask.cdl

# Generate grid: SeaRISE-Greenland-20km
sr_g20_searise.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating sr_g20_searise.nc: SeaRISE Greenland 20km grid (PISM-style indexing)'
	searise --icemodel searise

# Generate grid: ModelE - LonLat - Greenland - 2x2.5 degrees
modele_ll_g1qx1.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating modele_ll_g1qx1.nc: ModelE Atmosphere Grid'
	modele_ll --grid 1qx1 --zone g

# Overlap two grids
modele_ll_g1qx1-sr_g20_searise.nc : modele_ll_g1qx1.nc sr_g20_searise.nc
	echo '*****************************************************************'
	echo '[makefile] Overlapping ModelE and SeaRISE Grids'
	overlap modele_ll_g1qx1.nc sr_g20_searise.nc

pismsheet_g20_icebin_in.nc : modele_ll_g1qx1-sr_g20_searise.nc pismsheet_elev_mask.nc
	echo '*****************************************************************'
	echo '[makefile] Assembling IceBin Input File from grids.'
	$(PYTHON3) write_icebin_in_base.py . modele_ll_g1qx1 sr_g20_searise pismsheet_elev_mask.nc ./pismsheet_g20_icebin_in.nc

matrices.pik : pismsheet_g20_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Writing regridding matrices to matrices.pik'
	$(PYTHON3) write_matrices.py pismsheet_g20_icebin_in.nc

test_diagonal.png test_elevation.png : pismsheet_g20_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Testing that regridding matrices conserve; see test_diagonal.png and test_elevation.png'
	$(PYTHON3) test_conserv.py greenland pismsheet_g20_icebin_in.nc pismsheet_elev_mask.nc

test_correctA : pismsheet_g20_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Testing that the correctA flag works when generating regridding matrices; see test_correctA.png'
	$(PYTHON3) test_correctA.py

# =============== ModelE Input Files
GIC.144X90.DEC01.1.ext_1-fhc.nc Z1QX1fromZ1QX1N-fhc.nc : pismsheet_g20_icebin_in.nc
	$(PYTHON3) add_fhc.py --stieglitz --elev-mask-type mar --topo-leaf Z1QX1fromZ1QX1N --gic-leaf GIC.144X90.DEC01.1.ext_1 --icebin-in ./pismsheet_g20_icebin_in.nc --elev-mask ./pismsheet_elev_mask.nc

# =============== The actual example

# Grid outlines
sr_g20_searise.pdf : sr_g20_searise.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for SeaRISE Grid'
	$(PYTHON3) plot_grid_outlines.py sr_g20_searise grid

modele_ll_g1qx1.pdf : modele_ll_g1qx1.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for ModelE Grid'
	$(PYTHON3) plot_grid_outlines.py modele_ll_g1qx1 grid

modele_ll_g1qx1-sr_g20_searise.pdf : modele_ll_g1qx1-sr_g20_searise.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for Exchange Grid'
	$(PYTHON3) plot_grid_outlines.py modele_ll_g1qx1-sr_g20_searise exgrid



install:
	$(PYTHON3) install.py
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-legacy.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-sealand.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-ec.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py GIC.144X90.DEC01.1.ext_1_EC2.nc $(HOME)/modele_input/local



# Convert ETOPO1 file to NetCDF
# giss2nc --names FOCEAN --endian=big --input-file ZETOPO1.NCEI --output-file ZETOPO1.NCEI.nc &
