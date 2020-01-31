import os
import sys
import numpy as np
from giss.ncutil import copy_nc
import netCDF4
import argparse
from modele.constants import SHI,LHM,RHOI,RHOS,UI_ICEBIN,UI_NOTHING

parser = argparse.ArgumentParser(description='Convert GIC file for old snow/firn model to one for Stieglitz.')

parser.add_argument('igic',
    help="Name of classic GIC file to read")
parser.add_argument('--dir', '-d', dest='dir', default='.',
    help='Directory in which to look for input file and --output dir')
parser.add_argument('--output', '-o', dest='ogic', required=True,
    default=None,
    help="Name of output Stieglitz GIC file to write.  (Or directory if it ends in a slash)")
#parser.add_argument('--nlice', '-n', dest='nlice', type=int, default=5,
#    help="Number of layers to create in Stieglitz model")
nlice = 5    # Hard-coded for now

args = parser.parse_args()


os.chdir(args.dir)

if args.ogic.endswith(os.sep):   # User meant a directory
    if os.path.islink(args.igic):
        leaf = os.path.split(os.readlink(args.igic))[1]
    else:
        leaf = os.path.split(args.igic)[1]

    os.makedirs(args.ogic, exist_ok=True)
    ogic = os.path.join(args.ogic, os.path.splitext(leaf)[0] + '_stieglitz.nc')
else:
    ogic = args.ogic


gic2stieglitz.gic2stieglitz(args.igic, args.ogic, nlice)

