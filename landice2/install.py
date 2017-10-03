# Installs a netCDF file with the files/install_path convention
import sys
import os
from giss import ncutil

#ifname = sys.argv[1]
#odir = sys.argv[2]

odir = os.path.join(os.environ['HOME'], 'modele_input', 'local')

ncutil.install_nc('GIC.144X90.DEC01.1.ext_1_EC2.nc', odir)
ncutil.install_nc('Z2HX2fromZ1QX1N_EC2-legacy.nc', odir)
ncutil.install_nc('Z2HX2fromZ1QX1N_EC2-sealand.nc', odir)
ncutil.install_nc('Z2HX2fromZ1QX1N_EC2-ec.nc', odir)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

