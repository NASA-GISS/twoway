import numpy as np
import PIL
from PIL import Image  # Needed even though we choose to acces via PIL.Image
import netCDF4
from giss import runlength

"""Create a NetCDF file encoding the "Greenland Mask", an area
covering more than the Greenland island, but not any other land."""

ifname = 'focean1m_gmask_0.png'
ofname = 'gmask1m_0.nc'

# Load user-edited image
img = PIL.Image.open(ifname)
img = img.transpose(PIL.Image.FLIP_TOP_BOTTOM)

# Convert to Numpy array
mask = np.array(img)
mask1 = np.reshape(mask, -1)

# Get masked-out indices
indices = np.where(mask1 == 2)[0]
print(type(indices))
print(indices.dtype)

# Difference-encode
indices1 = np.zeros(indices.shape, dtype='i')
indices1[0] = indices[0]
indices1[1:] = indices[1:] - indices[:-1]

# Runlength encode
starts,runlens,runvals = runlength.rlencode(indices1)

# Store output, which should now be small
with netCDF4.Dataset(ofname, 'w') as nc:
    nc.createDimension('n', len(starts))
    nc.createVariable('starts', 'i', ('n',))[:] = starts
    nc.createVariable('runlens', 'i', ('n',))[:] = runlens
    nc.createVariable('runvals', 'i', ('n',))[:] = runvals
