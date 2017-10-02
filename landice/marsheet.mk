
# Set to your Python 3 command.  Should not need to be set if an
# appropriate Python3 environment module is already loaded.
PYTHON3 = python3

# Set this to the directory where your PISM spinup file resides.
# (NOT necessary to run the tests in this directory)
MAR_INPUT_DIR = /home/pmalexan/MARfiles

# --------------------------------------------------------------

# Run the main test.
all: test_diagonal.png test_elevation.png mar_g25_pism.pdf modele_ll_g2x2_5.pdf modele_ll_g2x2_5-mar_g25_pism.pdf matrices.pik GIC.144X90.DEC01.1.ext_1-fhc.nc Z2HX2fromZ1QX1N-fhc.nc

clean:
	rm *.nc *.pdf *.png

# =========== Generate stuff we check into git
# This requires external software (PISM), and should not normally need
# to be run.

# Files that will be checked into git
git_files : mar_elev_mask.cdl

.INTERMEDIATE : _mar_elev_mask.nc

# Extract topg, thk and mass from a PISM state file.
_mar_elev_mask.nc :
	$(PYTHON3) write_elev_mask.py $(MAR_INPUT_DIR)/MARv352_25km_mask_topo_pismStyle.nc _mar_elev_mask.nc

# Convert netCDF to text-based format
mar_elev_mask.cdl : _mar_elev_mask.nc
	ncdump -l 10 _mar_elev_mask.nc >mar_elev_mask.cdl

# ================ Generate input files for the example, from text antecedents

# Reconstitute topg, thk and mass
mar_elev_mask.nc : mar_elev_mask.cdl
	echo '*****************************************************************'
	echo '[makefile] Reconstituting elevation and land mask data (from MAR)'
	ncgen -o mar_elev_mask.nc mar_elev_mask.cdl

# Generate grid: MAR-Greenland-20km
mar_g25_pism.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating mar_g25_pism.nc: MAR Greenland 25km grid (PISM-style indexing)'
	mar

# Generate grid: ModelE - LonLat - Greenland - 2x2.5 degrees
modele_ll_g2x2_5.nc :
	echo '*****************************************************************'
	echo '[makefile] Generating modele_ll_g2x2_5.nc: ModelE Atmosphere Grid'
	modele_ll --zone g

# Overlap two grids
modele_ll_g2x2_5-mar_g25_pism.nc : modele_ll_g2x2_5.nc mar_g25_pism.nc
	echo '*****************************************************************'
	echo '[makefile] Overlapping ModelE and MAR Grids'
	overlap modele_ll_g2x2_5.nc mar_g25_pism.nc

mar_icebin_in.nc : modele_ll_g2x2_5-mar_g25_pism.nc mar_elev_mask.nc
	echo '*****************************************************************'
	echo '[makefile] Assembling IceBin Input File from grids.'
	$(PYTHON3) write_icebin_in_base.py . modele_ll_g2x2_5 mar_g25_pism mar_elev_mask.nc ./mar_icebin_in.nc

matrices.pik : mar_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Writing regridding matrices to matrices.pik'
	$(PYTHON3) write_matrices.py mar_icebin_in.nc

test_diagonal.png test_elevation.png : mar_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Testing that regridding matrices conserve; see test_diagonal.png and test_elevation.png'
	$(PYTHON3) test_conserv.py greenland mar_icebin_in.nc mar_elev_mask.nc

test_correctA : mar_icebin_in.nc
	echo '*****************************************************************'
	echo '[makefile] Testing that the correctA flag works when generating regridding matrices; see test_correctA.png'
	$(PYTHON3) test_correctA.py

# =============== ModelE Input Files
GIC.144X90.DEC01.1.ext_1-fhc.nc Z2HX2fromZ1QX1N-fhc.nc : mar_icebin_in.nc
	$(PYTHON3) add_fhc.py --stieglitz --elev-mask-type mar --topo-leaf Z2HX2fromZ1QX1N --gic-leaf GIC.144X90.DEC01.1.ext_1 --icebin-in ./mar_icebin_in.nc --elev-mask ./mar_elev_mask.nc

# =============== The actual example

# Grid outlines
mar_g25_pism.pdf : mar_g25_pism.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for MAR Grid'
	$(PYTHON3) plot_grid_outlines.py mar_g25_pism grid

modele_ll_g2x2_5.pdf : modele_ll_g2x2_5.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for ModelE Grid'
	$(PYTHON3) plot_grid_outlines.py modele_ll_g2x2_5 grid

modele_ll_g2x2_5-mar_g25_pism.pdf : modele_ll_g2x2_5-mar_g25_pism.nc
	echo '*****************************************************************'
	echo '[makefile] Plotting grid outlines for Exchange Grid'
	$(PYTHON3) plot_grid_outlines.py modele_ll_g2x2_5-mar_g25_pism exgrid



install:
	$(PYTHON3) install.py
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-legacy.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-sealand.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py Z2HX2fromZ1QX1N_EC2-ec.nc $(HOME)/modele_input/local
#	$(PYTHON3) install.py GIC.144X90.DEC01.1.ext_1_EC2.nc $(HOME)/modele_input/local
