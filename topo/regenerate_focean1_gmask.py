import numpy as np
import PIL
import netCDF4
from giss import runlength
from PIL import Image    # Necessary
import shutil

maskname = 'gmask1m.nc'
incname = 'ZETOPO1.NCEI.nc'
ivname = 'FOCEAN'
ofname = 'focean1m_gmask.png'
oncname = 'ZETOPO1.NCEI-SeparateGreenland.nc'

# Read continents from ETOPO1
with netCDF4.Dataset(incname) as nc:
    ncvar = nc.variables[ivname]
    focean1m = np.zeros(ncvar.shape, dtype=np.uint8)
    focean1m[:] = ncvar[:]

# Read mask
with netCDF4.Dataset(maskname) as nc:
    starts = nc.variables['starts'][:]
    runlens = nc.variables['runlens'][:]
    runvals = nc.variables['runvals'][:]

# Runlength decode
indices1 = runlength.rldecode(starts, runlens, runvals)

# Difference-decode to determine indices where Greenland is masked out
gindices = np.cumsum(indices1)

# Mask them out!
focean1m1 = focean1m.reshape(-1)
focean1m1[gindices] = 2

# ------------------------------------------------------
# Generate the NC file
print('Creating {}'.format(oncname))
shutil.copyfile(incname, oncname)
print('Updating {}'.format(oncname))
with netCDF4.Dataset(oncname, 'a') as nc:
    ncvar = nc.variables['FOCEAN']
    fo2 = ncvar[:]
    fo2[np.logical_and(focean1m==2, fo2==0)] = 2
    ncvar[:] = fo2

# ------------------------------------------------------
# Generate the PNG file

print('Saving the PNG file')

# Save it all to a PNG file
img = Image.fromarray(focean1m, mode='P')
img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)

# Create initial grayscale palette
palette = np.zeros((256,3), dtype='i')
for i in range(0,256):
    palette[i,:] = 255-i

# Replace certain colors
palette[0,:] = (0,255,0)        # FOCEAN=0 = Land
palette[1,:] = (0,0,255)        # 1 = Ocean
palette[2,:] = (255,255,255)    # 2 = Greenland

pl = list(palette.reshape(-1))
img.putpalette(pl)

img.save(ofname)
