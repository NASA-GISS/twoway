#!/bin/bash


cdo select,name=EOCEAN,ZICETOP,ZSOLIDG /discover/nobackup/projects/giss/prod_input_files/ZETOPO1.nc tmp1.nc

ncrename -d IM,im1m -d JMp1,jm1m_gridreg -v EOCEAN,FOCEAN -v ZSOLIDG,ZSOLID tmp1.nc tmp2.nc

cdo expr,'ZICTOP=ZICETOP+ZSOLID' tmp2.nc tmp3.nc

cdo merge tmp2.nc tmp3.nc tmp4.nc

ncks -x -v ZICETOP tmp4.nc ZETOPO1.NCEI.nc

rm tmp*.nc




