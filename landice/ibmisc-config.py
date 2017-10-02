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
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/blitz-1.0.0-f5m2jsss6vvt6azbgvwqmb6xgemlgi7x
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/boost-1.62.0-y4h7xx32yv4rqf3ncbop76phrxw4dfhb
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/bzip2-1.0.6-nawaab2hw2k32clgz7qrqz2k747hl36t
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libtool-2.4.6-q5ztpklzt3emeq3p7rqguoqyht5lac36
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/m4-1.4.17-kmufpwmhwys35ygpe5zcnxrzdy6dvm3e
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libsigsegv-2.10-ytewamh7ahdlne6piaaewv2pl2onj5lj
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pkg-config-0.29.1-zmirozyvyf5jfalrz5vgge2uydgjtviq
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/util-macros-1.19.0-36ec63zxfqtarj4wzuztzeckh6th53kp
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ncurses-6.0-h66uwdb6z2ixa3dxf34afrakrlyjffwz
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/eigen-3.2.10-2cbaqas5aj3c2ty4wavwopmb5i6bjxzo
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gmp-6.1.2-tl5w2mhmaszqxjlmdbsbywrfr2jmhm54
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mpfr-3.1.4-2igx7t2p5wxlg6iignrzio55hz5exsu7
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/scotch-6.0.4-clop2l7km2oqmxfmlwsnkmtpn4xz74ps
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/bison-3.0.4-qkwzrwhiza56midai42xbvamrl2tm4ze
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/flex-2.6.1-ufadjk4g4oviddkzilrpzhup2jvd2rls
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gettext-0.19.8.1-hpq5i6r6oaas73l7rvvj3gjspz7v7ava
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libxml2-2.9.4-lhr4cimddhzjn4q256vlpvj3ocqlowox
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/xz-5.2.2-zooqtth7v5bhx7mn4r3lelhpyeiw6adx
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/tar-1.29-hq2pmmutpu2t4n6xgdyjxnwy4hcbj7he
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/help2man-1.47.4-xv4z622cyl4oapcxkjhbrhxp3nuv6pdc
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/everytrace-develop-gyeos66xokjpztn4ez7cgmkzgftvtqfh
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/googletest-1.7.0-mdbsavkkz6fpc2xhh3q2qtiia3eeuxfm
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-cxx4-4.3.0-zeouiscr2ll5g7xcy6zf56w5ujkedr5x
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/autoconf-2.69-tbehzc4kv5ftiixquyikzg3o5vp62xpe
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-cython-0.23.5-j6fjvjhngoaymffempjt6vnsonxzfz5h
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/binutils-2.27-zlh4sb6ny2hcbxrfawdagniowjzlrdnm
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/python-3.5.2-twdmmviznl4lwbqmx3eifpl56z7no65n
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/readline-6.3-bbjtafhc2cmstqz6aa3jc5bhcdk67wwz
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/sqlite-3.8.5-7h5xpacrgd54pm4d3zppjh5ud5vceuaq
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-numpy-1.11.2-ingtf52klf75lja4tafbkfd5f3svtphf
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-nose-1.3.7-cyssdfvgroffdjxldbbirdtoxhnvppls
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-setuptools-25.2.0-jqf3eg2gqgo3j3z2gnju52rn3jfjro3y
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe
"""))
env['CXX'] = '/home2/rpfische/spack-tools/opt/spack/linux-x86_64/gcc-4.8.5/gcc-4.9.3-jfebnuuusdch34j7pvdnvlxffe2rmoe4/bin/g++'
env['FC'] = '/home2/rpfische/spack-tools/opt/spack/linux-x86_64/gcc-4.8.5/gcc-4.9.3-jfebnuuusdch34j7pvdnvlxffe2rmoe4/bin/gfortran'
env['PATH'] = ":".join(cmdlist("""
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/python-3.5.2-twdmmviznl4lwbqmx3eifpl56z7no65n/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-cxx4-4.3.0-zeouiscr2ll5g7xcy6zf56w5ujkedr5x/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-numpy-1.11.2-ingtf52klf75lja4tafbkfd5f3svtphf/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-cython-0.23.5-j6fjvjhngoaymffempjt6vnsonxzfz5h/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/everytrace-develop-gyeos66xokjpztn4ez7cgmkzgftvtqfh/bin
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/bin
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
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/blitz-1.0.0-f5m2jsss6vvt6azbgvwqmb6xgemlgi7x/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/boost-1.62.0-y4h7xx32yv4rqf3ncbop76phrxw4dfhb/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/bzip2-1.0.6-nawaab2hw2k32clgz7qrqz2k747hl36t/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libtool-2.4.6-q5ztpklzt3emeq3p7rqguoqyht5lac36/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/m4-1.4.17-kmufpwmhwys35ygpe5zcnxrzdy6dvm3e/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libsigsegv-2.10-ytewamh7ahdlne6piaaewv2pl2onj5lj/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/pkg-config-0.29.1-zmirozyvyf5jfalrz5vgge2uydgjtviq/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/util-macros-1.19.0-36ec63zxfqtarj4wzuztzeckh6th53kp/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ncurses-6.0-h66uwdb6z2ixa3dxf34afrakrlyjffwz/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/eigen-3.2.10-2cbaqas5aj3c2ty4wavwopmb5i6bjxzo/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gmp-6.1.2-tl5w2mhmaszqxjlmdbsbywrfr2jmhm54/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mpfr-3.1.4-2igx7t2p5wxlg6iignrzio55hz5exsu7/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/scotch-6.0.4-clop2l7km2oqmxfmlwsnkmtpn4xz74ps/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/bison-3.0.4-qkwzrwhiza56midai42xbvamrl2tm4ze/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/flex-2.6.1-ufadjk4g4oviddkzilrpzhup2jvd2rls/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gettext-0.19.8.1-hpq5i6r6oaas73l7rvvj3gjspz7v7ava/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libxml2-2.9.4-lhr4cimddhzjn4q256vlpvj3ocqlowox/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/xz-5.2.2-zooqtth7v5bhx7mn4r3lelhpyeiw6adx/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/tar-1.29-hq2pmmutpu2t4n6xgdyjxnwy4hcbj7he/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/help2man-1.47.4-xv4z622cyl4oapcxkjhbrhxp3nuv6pdc/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/everytrace-develop-gyeos66xokjpztn4ez7cgmkzgftvtqfh/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/googletest-1.7.0-mdbsavkkz6fpc2xhh3q2qtiia3eeuxfm/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-cxx4-4.3.0-zeouiscr2ll5g7xcy6zf56w5ujkedr5x/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/autoconf-2.69-tbehzc4kv5ftiixquyikzg3o5vp62xpe/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-cython-0.23.5-j6fjvjhngoaymffempjt6vnsonxzfz5h/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/binutils-2.27-zlh4sb6ny2hcbxrfawdagniowjzlrdnm/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/python-3.5.2-twdmmviznl4lwbqmx3eifpl56z7no65n/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/readline-6.3-bbjtafhc2cmstqz6aa3jc5bhcdk67wwz/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/sqlite-3.8.5-7h5xpacrgd54pm4d3zppjh5ud5vceuaq/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-numpy-1.11.2-ingtf52klf75lja4tafbkfd5f3svtphf/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-nose-1.3.7-cyssdfvgroffdjxldbbirdtoxhnvppls/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-setuptools-25.2.0-jqf3eg2gqgo3j3z2gnju52rn3jfjro3y/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/include
    /home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe/include
"""))

cmd = cmdlist("""
/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/cmake-3.7.1-f44ykg74y4woethb2gw5utad3rpkdn7e/bin/cmake
    -DCMAKE_INSTALL_PREFIX:PATH=/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ibmisc-develop-eqnywrtzozzyw7uvfjzb437lbajen4c3
    -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo
    -DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=FALSE
    -DCMAKE_INSTALL_RPATH:STRING=/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ibmisc-develop-eqnywrtzozzyw7uvfjzb437lbajen4c3/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ibmisc-develop-eqnywrtzozzyw7uvfjzb437lbajen4c3/lib64:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/blitz-1.0.0-f5m2jsss6vvt6azbgvwqmb6xgemlgi7x/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/boost-1.62.0-y4h7xx32yv4rqf3ncbop76phrxw4dfhb/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/bzip2-1.0.6-nawaab2hw2k32clgz7qrqz2k747hl36t/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openmpi-1.10.1-2ew2gg7hvoc7vj7fc4s6c3mdfeoblp76/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hwloc-1.11.4-nygoq6ckmmqmcs5yxbbopa7ogq7mzeb6/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/libpciaccess-0.13.4-a6hzhtgltaen6r4a226tur2chhdierl7/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/zlib-1.2.8-xsie4hdnoagbchdfk3envninapwcoozp/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/fftw-3.3.5-ikgs5nv3q7wxnsixm7slhgoj4j7pfcey/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/gmp-6.1.2-tl5w2mhmaszqxjlmdbsbywrfr2jmhm54/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/metis-5.1.0-3zcn2vzcg6gfyse7ybqo66ttcrfn4yen/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/mpfr-3.1.4-2igx7t2p5wxlg6iignrzio55hz5exsu7/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/scotch-6.0.4-clop2l7km2oqmxfmlwsnkmtpn4xz74ps/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/everytrace-develop-gyeos66xokjpztn4ez7cgmkzgftvtqfh/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-cxx4-4.3.0-zeouiscr2ll5g7xcy6zf56w5ujkedr5x/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/netcdf-4.4.1-as7nvfdulzo3lw5rdd4kwn33zpcpy2ki/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/hdf5-1.10.0-patch1-vjo6kk3i7nt3wfk7pnwulgk4b33zk76l/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/proj-4.9.2-54uiqru7o2ndyewznekplt3a4naxid5v/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-numpy-1.11.2-ingtf52klf75lja4tafbkfd5f3svtphf/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/openblas-0.2.19-qnfdxmfdkl7fdnfqgtxy32p4pngtb2tj/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/python-3.5.2-twdmmviznl4lwbqmx3eifpl56z7no65n/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/ncurses-6.0-h66uwdb6z2ixa3dxf34afrakrlyjffwz/lib:/usr/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/readline-6.3-bbjtafhc2cmstqz6aa3jc5bhcdk67wwz/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/sqlite-3.8.5-7h5xpacrgd54pm4d3zppjh5ud5vceuaq/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/udunits2-2.2.20-tjpaxgrlyqexjfqv5b4pijwdaila5euu/lib:/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/expat-2.2.0-gsmcyizz22wmkhqxi3fmd2jdugx4npbe/lib:/usr/lib64
    -DBUILD_PYTHON=YES
    -DUSE_EVERYTRACE=YES
    -DUSE_PROJ4=YES
    -DUSE_BLITZ=YES
    -DUSE_NETCDF=YES
    -DUSE_BOOST=YES
    -DUSE_UDUNITS2=YES
    -DUSE_GTEST=YES
    -DBUILD_DOCS=NO
    -DCYTHON_EXECUTABLE=/home2/rpfische/spack5/opt/spack/linux-centos7-x86_64/gcc-4.9.3/py-cython-0.23.5-j6fjvjhngoaymffempjt6vnsonxzfz5h/bin/cython
""") + sys.argv[1:]

proc = subprocess.Popen(cmd, env=env)
proc.wait()
