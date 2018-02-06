import numpy as np
import PIL
import netCDF4

from PIL import Image

img = PIL.Image.open('img.png')
img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)
#img = img.transpose(PIL.Image.ROTATE_270)

mask = np.array(img)

print('Image produces Numpy Array of dtype = ', mask.dtype)

with netCDF4.Dataset('x.nc', 'a') as nc:
    val = nc.variables['var00'][:]
    val[np.logical_and(mask==2, val==0)] = 2
    nc.variables['var00'][:] = val[:]
