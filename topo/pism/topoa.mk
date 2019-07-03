# General recipe for generating TOPO files from PISM state files.
# Uses 
#
# Inputs (to be symlinked):
#
# 1. local_ice_grid.nc: Local Ice Grid
# 2. pismsheet_elev_mask.nc: PISM state file

#Output:
#
# topoa.nc

all : topoa.nc

# ---------- Pre-computed items
#


../pism2_g20_pism2.nc :
	cd ..; $(MAKE) pism2_g20_pism2.nc

../../modele_ll_g1qx1.nc :
	cd ../..; $(MAKE) modele_ll_g1qx1.nc

../../global_ecO_ng.nc :
	cd ../..; $(MAKE) global_ecO_ng.nc

../../topoo_ng.nc :
	cd ../..; $(MAKE) topoo_ng.nc



# ----------------- Things we make here

modele_ll_g1qx1-pism2_g20_pism2.nc: ../../modele_ll_g1qx1.nc ../pism2_g20_pism2.nc
	overlap ../../modele_ll_g1qx1.nc ../pism2_g20_pism2.nc

gcmO.nc : modele_ll_g1qx1-pism2_g20_pism2.nc pismsheet_elev_mask.nc ../../modele_ll_g1qx1.nc ../pism2_g20_pism2.nc
	echo '*****************************************************************'
	echo '[makefile] Assembling IceBin Input File from grids (contains loadable gcmO).'
	python3 ../../write_icebin_in_base.py ../../modele_ll_g1qx1.nc ../pism2_g20_pism2.nc modele_ll_g1qx1-pism2_g20_pism2.nc pismsheet_elev_mask.nc ./gcmO.nc


topoo_merged.nc : pismsheet_elev_mask.nc gcmO.nc ../../global_ecO_ng.nc ../../topoo_ng.nc
	make_merged_topoo --topoo_merged topoo_merged.nc --elevmask pism:pismsheet_elev_mask.nc --gcmO gcmO.nc --global_ecO ../../global_ecO_ng.nc --topoo ../../topoo_ng.nc


topoa_nc4.nc : topoo_merged.nc
	make_topoa -o topoa_nc4.nc --global_ecO topoo_merged.nc --topoo topoo_merged.nc 2>err

topoa.nc : topoa_nc4.nc
	nccopy -k classic topoa_nc4.nc topoa.nc
