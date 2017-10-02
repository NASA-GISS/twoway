#!/bin/python
#
# /home2/rpfische/spack5/bin/spack -c ~/spscopes/centos7 -c ~/spscopes/gissversions -c ~/spscopes/twoway -c ~/spscopes/develop install -I --report --setup modele --setup ibmisc --setup pism --setup icebin modele

import sys
import os
import subprocess

def cmdlist(str):
    return list(x.strip().replace("'",'') for x in str.split('\n') if x)
env = dict(os.environ)
env['CC'] = '/home2/rpfische/spack-tools/opt/spack/linux-x86_64/gcc-4.8.5/gcc-4.9.3-jfebnuuusdch34j7pvdnvlxffe2rmoe4/bin/gcc'
env['CMAKE_PREFIX_PATH'] = ":".join(cmdlist("""
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ncurses-6.0-h66uwdb6z2ixa3dxf34afrakrlyjffwz
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libtool-2.4.6-q5ztpklzt3emeq3p7rqguoqyht5lac36
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/m4-1.4.17-kmufpwmhwys35ygpe5zcnxrzdy6dvm3e
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libsigsegv-2.10-ytewamh7ahdlne6piaaewv2pl2onj5lj
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pkg-config-0.29.1-zmirozyvyf5jfalrz5vgge2uydgjtviq
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/util-macros-1.19.0-36ec63zxfqtarj4wzuztzeckh6th53kp
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gsl-2.3-5qnos74efitt5lzzmn64mfv66v4mc4qz
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/petsc-3.7.4-k3syjviy2nud4jq2e7eo4fr7ie4kwu4p
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hypre-2.11.1-ehjwhs7wngo57md5slzyib256enpybba
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mumps-5.0.2-nt3b5judrdvmj5iujat3nld4kt6hfswi
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netlib-scalapack-2.0.2-55r2m7hz6lwe6bdjkq5i6povtj4nzldf
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/parmetis-4.0.3-t6ftobmut3gp336udzilwbsd6nepevjj
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/superlu-dist-5.1.1-lezx2ypykxxiengvdd4pa2vxhhtmyj42
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe
"""))
env['CXX'] = '/home2/rpfische/spack-tools/opt/spack/linux-x86_64/gcc-4.8.5/gcc-4.9.3-jfebnuuusdch34j7pvdnvlxffe2rmoe4/bin/g++'
env['FC'] = '/home2/rpfische/spack-tools/opt/spack/linux-x86_64/gcc-4.8.5/gcc-4.9.3-jfebnuuusdch34j7pvdnvlxffe2rmoe4/bin/gfortran'
env['PATH'] = ":".join(cmdlist("""
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/petsc-3.7.4-k3syjviy2nud4jq2e7eo4fr7ie4kwu4p/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gsl-2.3-5qnos74efitt5lzzmn64mfv66v4mc4qz/bin
    /home2/rpfische/sh
    /home2/rpfische/opt/smartgit/bin
    /home2/rpfische/spack5/bin
    /usr/local/sbin
    /usr/local/bin
    /sbin
    /bin
    /usr/sbin
    /usr/bin
    /root/bin
    /usr/local/git/bin
    /home2/rpfische/.local/bin
    /home2/rpfische/bin
"""))
env['SPACK_TRANSITIVE_INCLUDE_PATH'] = ";".join(cmdlist("""
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ncurses-6.0-h66uwdb6z2ixa3dxf34afrakrlyjffwz/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libtool-2.4.6-q5ztpklzt3emeq3p7rqguoqyht5lac36/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/m4-1.4.17-kmufpwmhwys35ygpe5zcnxrzdy6dvm3e/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libsigsegv-2.10-ytewamh7ahdlne6piaaewv2pl2onj5lj/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pkg-config-0.29.1-zmirozyvyf5jfalrz5vgge2uydgjtviq/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/util-macros-1.19.0-36ec63zxfqtarj4wzuztzeckh6th53kp/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gsl-2.3-5qnos74efitt5lzzmn64mfv66v4mc4qz/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/petsc-3.7.4-k3syjviy2nud4jq2e7eo4fr7ie4kwu4p/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hypre-2.11.1-ehjwhs7wngo57md5slzyib256enpybba/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mumps-5.0.2-nt3b5judrdvmj5iujat3nld4kt6hfswi/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netlib-scalapack-2.0.2-55r2m7hz6lwe6bdjkq5i6povtj4nzldf/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/parmetis-4.0.3-t6ftobmut3gp336udzilwbsd6nepevjj/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/superlu-dist-5.1.1-lezx2ypykxxiengvdd4pa2vxhhtmyj42/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe/include
"""))

cmd = cmdlist("""
/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/bin/cmake
    -DCMAKE_INSTALL_PREFIX:PATH=/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pism-dev-kkl2u4yp2rjcfu7cyozlbldntkarer5l
    -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=FALSE
    -DCMAKE_INSTALL_RPATH:STRING=/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pism-dev-kkl2u4yp2rjcfu7cyozlbldntkarer5l/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pism-dev-kkl2u4yp2rjcfu7cyozlbldntkarer5l/lib64:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gsl-2.3-5qnos74efitt5lzzmn64mfv66v4mc4qz/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/petsc-3.7.4-k3syjviy2nud4jq2e7eo4fr7ie4kwu4p/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hypre-2.11.1-ehjwhs7wngo57md5slzyib256enpybba/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mumps-5.0.2-nt3b5judrdvmj5iujat3nld4kt6hfswi/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netlib-scalapack-2.0.2-55r2m7hz6lwe6bdjkq5i6povtj4nzldf/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/parmetis-4.0.3-t6ftobmut3gp336udzilwbsd6nepevjj/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/superlu-dist-5.1.1-lezx2ypykxxiengvdd4pa2vxhhtmyj42/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe/lib
    -DPism_BUILD_EXTRA_EXECS=NO
    -DBUILD_SHARED_LIBS=YES
    -DPism_BUILD_PYTHON_BINDINGS=NO
    -DPism_BUILD_ICEBIN=YES
    -DPism_USE_PROJ4=YES
    -DPism_USE_PARALLEL_NETCDF4=NO
    -DPism_USE_PNETCDF=NO
    -DPism_USE_PARALLEL_HDF5=NO
    -DPism_BUILD_PDFS=NO
""") + sys.argv[1:]

proc = subprocess.Popen(cmd, env=env)
proc.wait()
