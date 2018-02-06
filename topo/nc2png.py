import numpy as np
import PIL
import netCDF4

from PIL import Image

#fname = 'ZNGDC1.nc'
#vname = 'FCONT1'

#fname = 'Z2MX2M.NGDC.nc'
#vname = 'FOCEN2'

fname = '/home2/rpfische/modele_input/origin/ZETOPO1.NCEI.nc'
vname = 'var00'


with netCDF4.Dataset(fname) as nc:
    ncvar = nc.variables[vname]
    val_i = np.zeros(ncvar.shape, dtype=np.uint8)
    val_i[:] = ncvar[:]

img = Image.fromarray(val_i, mode='P')

#img = img.transpose(PIL.Image.ROTATE_180)
img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)

# Create initial grayscale palette
palette = np.zeros((256,3), dtype='i')
for i in range(0,256):
    palette[i,:] = 255-i

# Replace certain colors
palette[0,:] = (0,0,255)        # FCONT=0 = Ocean
palette[1,:] = (0,255,0)        # 1 = Land
palette[2,:] = (255,255,255)    # 2 = Greenland


pl = list(palette.reshape(-1))
print(pl)
img.putpalette(pl)


img.save('img.png')

print(img.getbands())
