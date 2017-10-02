all : out.g20km_10ka

std-greenland :
	(cd $(PISM_PREFIX)/share/pism/examples; tar cf - std-greenland) | (tar xvf -)
	cd std-greenland; ln -s ../std-greenland.mk makefile

