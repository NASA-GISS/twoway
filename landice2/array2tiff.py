import netCDF4
import numpy as np
from PIL import Image


# https://stackoverflow.com/questions/7569553/working-with-tiffs-import-export-in-python-using-numpy

fname = '/home2/rpfische/modele_input/origin/ZETOPO1.NCEI.nc'
vname  'var00'





imarray = np.zeros((100,200), dtype=np.uint8)
print(imarray.shape)

for j in range(0, imarray.shape[0]):
    for i in range(0, imarray.shape[1]):
        imarray[j,i] = j+i

# http://pillow.readthedocs.io/en/3.1.x/handbook/concepts.html#concept-modes
img = Image.fromarray(imarray, mode='P')

img.putpalette([
    0,0,0,
    255,0,0,
    0,255,0,
])


img.save('test.tiff')
