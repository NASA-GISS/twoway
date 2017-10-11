import os
srcdir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(os.path.join(srcdir, '..', '..', 'python', 'lib'))

import copy
import numpy as np
from giss import giutil
import icebin
from icebin import ibgrid
from giss.ncutil import copy_nc
import netCDF4
import argparse
from modele.constants import SHI,LHM,RHOI,RHOS,UI_ICEBIN,UI_NOTHING
import scipy.sparse
import itertools

CC = [(10852,43592), (10852,43593), (10853,43306), (10853,43307), (10853,43594),
(10853,43595), (10854,43308), (10854,43309), (10854,43596), (10854,43597),
(10855,43598), (10995,43879), (10995,44166), (10995,44167), (10996,43880),
(10996,43881), (10996,44168), (10996,44169), (10997,43882), (10997,43883),
(10997,44170), (10997,44171), (10998,43884), (10998,43885), (10998,44172),
(10998,44173), (10999,43886), (10999,43887), (10999,44174), (10999,44175),
(11139,44454), (11139,44455), (11139,44743), (11140,44456), (11140,44457),
(11140,44744), (11140,44745), (11141,44458), (11141,44459), (11141,44746),
(11141,44747), (11142,44460), (11142,44461), (11142,44748), (11142,44749),
(11143,44462), (11143,44463), (11143,44750), (11143,44751), (11144,44464),
(11144,44752), (11144,44753), (11145,44754), (11283,45031), (11283,45319),
(11284,45032), (11284,45033), (11284,45320), (11284,45321), (11285,45034),
(11285,45035), (11285,45322), (11285,45323), (11286,45036), (11286,45037),
(11286,45324), (11286,45325), (11287,45038), (11287,45039), (11287,45326),
(11287,45327), (11288,45040), (11288,45041), (11288,45328), (11288,45329),
(11289,45042), (11289,45043), (11289,45330), (11289,45331), (11290,45044),
(11290,45045), (11290,45332), (11290,45333), (11291,45334), (11427,45606),
(11427,45607), (11427,45894), (11427,45895), (11428,45608), (11428,45609),
(11428,45896), (11428,45897), (11429,45610), (11429,45611), (11429,45898),
(11429,45899), (11430,45612), (11430,45613), (11430,45900), (11430,45901),
(11431,45614), (11431,45615), (11431,45902), (11431,45903), (11432,45616),
(11432,45617), (11432,45904), (11432,45905), (11433,45618), (11433,45619),
(11433,45906), (11433,45907), (11434,45620), (11434,45621), (11434,45908),
(11434,45909), (11435,45622), (11435,45623), (11435,45910), (11435,45911),
(11436,45624), (11436,45912), (11570,46181), (11570,46469), (11571,46182),
(11571,46183), (11571,46470), (11571,46471), (11572,46184), (11572,46185),
(11572,46472), (11572,46473), (11573,46186), (11573,46187), (11573,46474),
(11573,46475), (11574,46188), (11574,46189), (11574,46476), (11574,46477),
(11575,46190), (11575,46191), (11575,46478), (11575,46479), (11576,46192),
(11576,46193), (11576,46480), (11576,46481), (11577,46194), (11577,46195),
(11577,46482), (11577,46483), (11578,46196), (11578,46197), (11578,46484),
(11578,46485), (11579,46198), (11579,46199), (11579,46486), (11579,46487),
(11580,46200), (11580,46201), (11580,46488), (11580,46489), (11581,46202),
(11581,46490), (11713,46754), (11713,46755), (11713,47042), (11713,47043),
(11714,46756), (11714,46757), (11714,47044), (11714,47045), (11715,46758),
(11715,46759), (11715,47046), (11715,47047), (11716,46760), (11716,46761),
(11716,47048), (11716,47049), (11717,46762), (11717,46763), (11717,47050),
(11717,47051), (11718,46764), (11718,46765), (11718,47052), (11718,47053),
(11719,46766), (11719,46767), (11719,47054), (11719,47055), (11720,46768),
(11720,46769), (11720,47056), (11720,47057), (11721,46770), (11721,46771),
(11721,47058), (11721,47059), (11722,46772), (11722,46773), (11722,47060),
(11722,47061), (11723,46774), (11723,46775), (11723,47062), (11723,47063),
(11724,46776), (11724,46777), (11724,47064), (11724,47065), (11725,46778),
(11725,47066), (11854,47613), (11855,47614), (11855,47615), (11856,47329),
(11856,47616), (11856,47617), (11857,47330), (11857,47331), (11857,47618),
(11857,47619), (11858,47332), (11858,47333), (11858,47620), (11858,47621),
(11859,47334), (11859,47335), (11859,47622), (11859,47623), (11860,47336),
(11860,47337), (11860,47624), (11860,47625), (11861,47338), (11861,47339),
(11861,47626), (11861,47627), (11862,47340), (11862,47341), (11862,47628),
(11862,47629), (11863,47342), (11863,47343), (11863,47630), (11863,47631),
(11864,47344), (11864,47345), (11864,47632), (11864,47633), (11865,47346),
(11865,47347), (11865,47634), (11865,47635), (11866,47348), (11866,47349),
(11866,47636), (11866,47637), (11867,47350), (11867,47351), (11867,47638),
(11867,47639), (11868,47352), (11868,47353), (11868,47640), (11868,47641),
(11869,47354), (11869,47355), (11869,47642), (11869,47643), (11870,47356),
(11870,47357), (11870,47644), (11870,47645), (11871,47358), (11871,47646),
(11994,48181), (11995,47895), (11995,48182), (11995,48183), (11996,47896),
(11996,47897), (11996,48184), (11996,48185), (11997,47898), (11997,47899),
(11997,48186), (11997,48187), (11998,47900), (11998,47901), (11998,48188),
(11998,48189), (11999,47902), (11999,47903), (11999,48190), (11999,48191),
(12000,47904), (12000,47905), (12000,48192), (12000,48193), (12001,47906),
(12001,47907), (12001,48194), (12001,48195), (12002,47908), (12002,47909),
(12002,48196), (12002,48197), (12003,47910), (12003,47911), (12003,48198),
(12003,48199), (12004,47912), (12004,47913), (12004,48200), (12004,48201),
(12005,47914), (12005,47915), (12005,48202), (12005,48203), (12006,47916),
(12006,47917), (12006,48204), (12006,48205), (12007,47918), (12007,47919),
(12007,48206), (12007,48207), (12008,47920), (12008,47921), (12008,48208),
(12008,48209), (12009,47922), (12009,47923), (12009,48210), (12009,48211),
(12010,47924), (12010,47925), (12010,48212), (12010,48213), (12011,47926),
(12011,47927), (12011,48214), (12011,48215), (12012,47928), (12012,47929),
(12012,48216), (12012,48217), (12013,47930), (12013,47931), (12013,48218),
(12013,48219), (12014,47932), (12014,47933), (12014,48220), (12014,48221),
(12015,47934), (12015,48222), (12015,48223), (12138,48469), (12139,48470),
(12139,48471), (12140,48472), (12140,48473), (12140,48761), (12141,48474),
(12141,48475), (12141,48762), (12141,48763), (12142,48476), (12142,48477),
(12142,48764), (12142,48765), (12143,48478), (12143,48479), (12143,48766),
(12143,48767), (12144,48480), (12144,48481), (12144,48768), (12144,48769),
(12145,48482), (12145,48483), (12145,48770), (12145,48771), (12146,48484),
(12146,48485), (12146,48772), (12146,48773), (12147,48486), (12147,48487),
(12147,48774), (12147,48775), (12148,48488), (12148,48489), (12148,48776),
(12148,48777), (12149,48490), (12149,48491), (12149,48778), (12149,48779),
(12150,48492), (12150,48493), (12150,48780), (12150,48781), (12151,48494),
(12151,48495), (12151,48782), (12151,48783), (12152,48496), (12152,48497),
(12152,48784), (12152,48785), (12153,48498), (12153,48499), (12153,48786),
(12153,48787), (12154,48500), (12154,48501), (12154,48788), (12154,48789),
(12155,48502), (12155,48503), (12155,48790), (12155,48791), (12156,48504),
(12156,48505), (12156,48792), (12156,48793), (12157,48506), (12157,48507),
(12157,48794), (12157,48795), (12158,48508), (12158,48509), (12158,48796),
(12158,48797), (12159,48510), (12159,48511), (12159,48798), (12159,48799),
(12160,48512), (12160,48513), (12160,48800), (12160,48801), (12286,49053),
(12287,49054), (12287,49055), (12287,49343), (12288,49056), (12288,49057),
(12288,49344), (12288,49345), (12289,49058), (12289,49059), (12289,49346),
(12289,49347), (12290,49060), (12290,49061), (12290,49348), (12290,49349),
(12291,49062), (12291,49063), (12291,49350), (12291,49351), (12292,49064),
(12292,49065), (12292,49352), (12292,49353), (12293,49066), (12293,49067),
(12293,49354), (12293,49355), (12294,49068), (12294,49069), (12294,49356),
(12294,49357), (12295,49070), (12295,49071), (12295,49358), (12295,49359),
(12296,49072), (12296,49073), (12296,49360), (12296,49361), (12297,49074),
(12297,49075), (12297,49362), (12297,49363), (12298,49076), (12298,49077),
(12298,49364), (12298,49365), (12299,49078), (12299,49079), (12299,49366),
(12299,49367), (12300,49080), (12300,49081), (12300,49368), (12300,49369),
(12301,49082), (12301,49083), (12301,49370), (12302,49084), (12302,49085),
(12303,49086), (12304,49088), (12304,49089), (12304,49377), (12305,49090),
(12305,49378), (12305,49379), (12306,49380), (12306,49381), (12307,49382),
(12307,49383), (12435,49638), (12435,49639), (12438,49645), (12439,49646),
(12439,49647), (12440,49648), (12440,49649), (12441,49650)]


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def load_icebin_in(fname, sheetname):
    """Loads an IceBin setup for the Ocean <--> Ice Grids"""
    ret = dict()

    mm = icebin.GCMRegridder(fname)
    rm = mm.regrid_matrices(sheetname)

    with netCDF4.Dataset(fname) as nc:
        indexingI = ibgrid.Indexing(nc, 'm.greenland.gridI.indexing')
        indexingA = ibgrid.Indexing(nc, 'm.gridA.indexing')
        indexingHC = ibgrid.Indexing(nc, 'm.indexingHC')
        hcdefs = nc.variables['m.hcdefs'][:]
        nhc = len(nc.dimensions['m.nhc'])
        indexA_sub = nc.variables['m.gridA.cells.index'][:]
        areaA_sub = nc.variables['m.gridA.cells.native_area'][:]
        nA1 = getattr(nc.variables['m.gridA.info'], 'cells.nfull')

    areaA1 = np.zeros((nA1,))
    areaA1[indexA_sub] = areaA_sub    # Native area of full grid cell (on sphere)


    ret['mm'] = mm
    ret['rm'] = rm
    ret['indexingHC'] = indexingHC
    ret['indexingA'] = indexingA
    ret['hcdefs'] = hcdefs
    ret['nhc'] = nhc
    ret['areaA1'] = areaA1    # Native area of full grid cell
    ret['indexingI'] = indexingI

    return Struct(**ret)



parser = argparse.ArgumentParser(description='Produce elevation-classified input files')
#parser.add_argument('--topo-leaf', dest='topo',
#    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
#parser.add_argument('--gic-leaf', dest='gic',
#    help="Name of TOPO file without the 'nc' (will be found in MODELE_FILE_PATH)")
parser.add_argument('--icebin-in', dest='icebin_in',
    default='pismsheet_g20_icebin_in.nc',
    help="Name of IceBin input file")
parser.add_argument('--elev-mask', dest='elev_mask',
    default='pismsheet_elev_mask.nc',
    help="name of elevation / mask file from the high-res ice sheet (extract of a PISM file).")
#parser.add_argument('--elev-mask-type', dest='elev_mask_type',
#    help="File type for elev-mask: pism, mar")
#parser.add_argument('--stieglitz', action='store_true', default=False,
#    help="Set to generate initial conditions for Stieglitz model")

args = parser.parse_args()

# --------------------------------
ibinO = load_icebin_in(args.icebin_in, 'greenland')

# Regrid to fxoceanOp  (PISM fcont)
OvI = ibinO.rm.matrix('AvI', scale=False, correctA=False)    # WeightedSparse
OvI_correct = ibinO.rm.matrix('AvI', scale=False, correctA=True)

# Don't need to set up the mask on I ourselves; this is already
# built into the OvI matrix.
print('OvI.shape', OvI.shape)
fcontI = np.ones(OvI.shape[1])

# Scaling for O grid cells (that we know about)
# fill=1 ensures that grid cells we don't know about won't
# be touched in the scaling matrix
sO = 1. / ibinO.mm.wA('greenland', 'proj', fill=1.)

# Convert O <- I
fcontOp = sO * OvI.apply(fcontI, 0.)
fcontOp = np.round(fcontOp, decimals=12)

neg = fcontOp[fcontOp < 0]
print('neg', neg)

# Round fcontOp (PISM) to get fcontOm (ModelE)
fcontOm = np.round(fcontOp)

# Store it for debugging viewing
fcontOp2 = fcontOp.reshape(ibinO.indexingA.shape)    # Row-major shape
fcontOm2 = fcontOm.reshape(ibinO.indexingA.shape)    # Row-major shape
#with netCDF4.Dataset('x.nc', 'w') as nc:
#    nc.createDimension('jm', ibinO.indexingA.shape[0])
#    nc.createDimension('im', ibinO.indexingA.shape[1])
#    fcontOp_nc = nc.createVariable('fcontOp', 'd', ('jm', 'im'))
#    fcontOm_nc = nc.createVariable('fcontOm', 'd', ('jm', 'im'))
#
#    fcontOp_nc[:] = fcontOp2[:]
#    fcontOm_nc[:] = fcontOm2[:]

# Convert to focean
foceanOp = 1. - fcontOp
foceanOm = 1. - fcontOm


# Construct a regridder to the Atmosphere grid
mmA = ibinO.mm.to_modele(foceanOp, foceanOm)

# ---------------------------------------------
rmA = mmA.regrid_matrices('greenland')
print('xxxxxxxxxxxxxxxx222')
wAAm, AAmvIp, wIp = rmA.matrix('AAmvIp', scale=True, correctA=False)()

print(wAAm.shape)
print(wIp.shape)

wOvI,_,_ = OvI()
wOvI_correct,_,_ = OvI_correct()


sum_wIp = np.nansum(wIp)
sum_wOvI = np.nansum(wOvI)
sum_wOvI_correct = np.nansum(wOvI_correct)
sum_wAAm = np.nansum(wAAm)
sum_fcontOp = np.sum(fcontOp * ibinO.areaA1)
sum_fcontOm = np.sum(fcontOm * ibinO.areaA1)

if False:
    self.assertAlmostEqual(sum_wIp, sum_wOvI)
    self.assertAlmostEqual(sum_wOvI_correct, sum_fcontOp)
    self.assertAlmostEqual(sum_wAAm, sum_fcontOm)

print('wIp', sum_wIp, sum_wOvI)
print('fcontOp', sum_fcontOp, sum_wOvI_correct)
print('fcontOm', sum_fcontOm, sum_wAAm)



# Store for viewing
with netCDF4.Dataset('x.nc', 'w') as nc:
    nc.createDimension('jmO', ibinO.indexingA.shape[0])
    nc.createDimension('imO', ibinO.indexingA.shape[1])
    nc.createDimension('nx', ibinO.indexingI.shape[0])
    nc.createDimension('ny', ibinO.indexingI.shape[1])
    nc.createDimension('jmA', ibinO.indexingA.shape[0]/2)
    nc.createDimension('imA', ibinO.indexingA.shape[1]/2)

    fcontOp_nc = nc.createVariable('fcontOp', 'd', ('jmO', 'imO'))
    fcontOm_nc = nc.createVariable('fcontOm', 'd', ('jmO', 'imO'))
    wIp_nc = nc.createVariable('wIp', 'd', ('nx', 'ny'))
    wAAm_nc = nc.createVariable('wAAm', 'd', ('jmA', 'imA'))

    fcontOp_nc[:] = fcontOp2[:]
    fcontOm_nc[:] = fcontOm2[:]
    wIp_nc[:] = wIp[:]
    print('shape', wAAm_nc.shape, wAAm.shape, wIp.shape)
    wAAm_nc[:] = wAAm[:]

if False:
    for ix,(i,j,v) in enumerate(zip(AAmvIp.row, AAmvIp.col, AAmvIp.data)):
        print(i,j,v)
        if ix > 20: break



#diff = fcontOm - wAAm
#print(diff)

if False:
    for iA,group in itertools.groupby(CC, lambda x: x[0]):
        iOs = [x[1] for x in group]
        wOs = fcontOm[iOs] * ibinO.areaA1[iOs]
        #wOs = fcontOm[iOs]
        print('wAAm[{}]={} --> fcontOm{}={}={}'.format(iA,wAAm[iA], iOs, wOs, np.sum(wOs)))
