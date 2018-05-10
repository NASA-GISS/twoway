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
with netCDF4.Dataset(incname, 'r') as ncin:
    with netCDF4.Dataset(oncname, 'w') as ncout:

        first = True
        for vname in ('FOCEAN', 'ZICTOP', 'ZSOLID'):
            val1m_gridreg = ncin.variables[vname][:]

            # Convert grid-registered to pixel-registerd
            # We can fudge that by just dropping the last point
            # 1-minute is so small it won't make much difference for global
            # (The first row at the south pole has problems.  The last
            # row at the north pole does not.)
            val1m = val1m_gridreg[1:,:]

            # Create new dimensions
            if first:
                jm1m_d = ncout.createDimension('jm1m', size=val1m.shape[0])
                im1m_d = ncout.createDimension('im1m', size=val1m.shape[1])

            # Create variable
            ncvar = ncout.createVariable(vname, 'd', ('jm1m', 'im1m'))
            ncvar[:] = val1m[:]

            first = False

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
