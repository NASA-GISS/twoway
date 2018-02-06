import numpy as np
import PIL
import netCDF4

from PIL import Image

ifname = 'ZETOPO1.NCEI.nc'
ivname = 'FOCEAN'
ofname = 'focean1m.png'

with netCDF4.Dataset(ifname) as nc:
    ncvar = nc.variables[ivname]
    val_i = np.zeros(ncvar.shape, dtype=np.uint8)
    val_i[:] = ncvar[:]

img = Image.fromarray(val_i, mode='P')
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
