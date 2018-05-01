#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np                         
import matplotlib.pyplot as plt            
from matplotlib import cm                  
import matplotlib.colors as mcolors         
import h5py                                 
import sys                                  
import os 
import glob
from pprint import pprint
import calendar
import dateutil
import FLEXPART_PES_NETCARE_module as PES
import argparse


dfolder  = '/Users/mcallister/projects/flexpart/INP1_20140714/Output/FNL/'
p_header = os.path.join(dfolder,'header' )
p_data   = os.path.join(dfolder,'grid_time_20140714130200.nc')


##look at the main Flexpart output .nc file
f_tracer = h5py.File(p_data, mode = 'r')

##get grid and dimension information
xlat = PES.get_var(p_data, 'latitude')
Nlat = len(xlat)

xlon = PES.get_var(p_data, 'longitude')
Nlon = len(xlon)

ztop = PES.get_var(p_data, 'height') 
Ntop = len(ztop)

times = PES.get_var(p_data, 'time')
Ntimes = times.shape[0] #same as len(times)

ageclass = PES.get_var(p_data, 'nageclass')
Nage = len(ageclass)

releases = PES.get_var(p_data, 'numpoint')
Nrel = len(releases)

dimlist = [Ntimes, Nage, Nrel, Ntop, Nlat, Nlon]
print("Dimensions of CONC variable = " + str(dimlist))


##get PES(residence time) 3D and 2D arrays
Conc = PES.getTracerReflexible(p_data, 'spec001_mr', dimlist, Ntimes) #put Ntimes here for the whole amount of time, or (e.g.,) 5700 for 4 days back, note: Conc is the vertically resolved PES, a 3D array
Conc_tCol = np.sum(Conc, axis=0)

temp1 = Conc[0:4,:,:]
Conc_pCol300 = np.sum(temp1, axis=0)
del(temp1)

temp2 = Conc[0:1,:,:]
Conc_pCol10 = np.sum(temp2, axis=0)
del(temp2)

temp3 = Conc[0:2,:,:]
Conc_pCol100 = np.sum(temp3, axis=0)
del(temp3)

temp4 = Conc[0:3,:,:]
Conc_pCol200 = np.sum(temp4, axis=0)
del(temp4)

temp5 = Conc[0:5,:,:]
Conc_pCol500 = np.sum(temp5, axis=0)
del(temp5)


##Save all three outputs to an HDF5 file
outfile = dfolder + "summedPES.h5" #change the output file name when changing total summing time

outHDF5 = h5py.File(outfile, mode = 'w') 
outHDF5.create_dataset('Conc_tsum', data = Conc)
outHDF5.create_dataset('Conc_tCol', data = Conc_tCol)
outHDF5.create_dataset('Conc_pCol300', data = Conc_pCol300)
outHDF5.create_dataset('Conc_pCol10', data = Conc_pCol10)
outHDF5.create_dataset('Conc_pCol100', data = Conc_pCol100)
outHDF5.create_dataset('Conc_pCol200', data = Conc_pCol200)
outHDF5.create_dataset('Conc_pCol500', data = Conc_pCol500)

outHDF5.close()
print("Finished.")

