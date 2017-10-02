all : g20km_10ka.nc

pism_Greenland_5km_v1.1.nc :
	./preprocess.sh

g20km_10ka.nc : pism_Greenland_5km_v1.1.nc
	nice ./spinup.sh 12 const 10000 20 sia g20km_10ka.nc &> out.g20km_10ka
