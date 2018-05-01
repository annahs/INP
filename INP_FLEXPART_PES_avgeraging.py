#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import os
import numpy as np                         
import matplotlib.pyplot as plt            
from matplotlib import cm                  
import matplotlib.colors as mcolors         
from mpl_toolkits.basemap import Basemap  
import h5py 
import FLEXPART_PES_NETCARE_module as PES
import INP_source_apportionment_module as INP 
import dateutil
import argparse
import glob
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import Alert_sampling_times as AL



sample_type = 'INP25'
case = 'highest'

sample_times, desc 	= AL.getHours(sample_type,case,number_samples=2)
#sample_times = [
#[17, '03/27/2016 16:45', '03/27/2016 18:45', 0.518718759],	
#[18, '03/28/2016 13:55', '03/28/2016 15:56', 0.541414483],	
#] 
#
#samples = [row[0] for row in sample_times]
#desc = desc + str(samples)

avgd_PES 			= INP.getAveragedAlert2016PES(sample_times)

###Save avgd outputs to an HDF5 file
#base_path = '/Volumes/storage/FLEXPART/Alert_2016/FLEXPART_2016_dkunkel/'
#outfile = base_path + 'FLEXPART_avgdPES_0-100m_Alert2016_' + desc + ".h5" 
#outHDF5 = h5py.File(outfile, mode = 'w') 
#outHDF5.create_dataset('avgd_PES', data = avgd_PES)
#outHDF5.close()
#
###Save grid to an HDF5 file
#outfile = base_path + 'FLEXPART_grid.h5' 
#outHDF5 = h5py.File(outfile, mode = 'w') 
#outHDF5.create_dataset('xlon', data = xlon)
#outHDF5.create_dataset('xlat', data = xlat)
#outHDF5.close()
#print 'saved'


###plots
#define the figure
fig = plt.figure(figsize=(10,10))

#create a basemap instance
m = Basemap(width=10000000,height=10000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.)

#re-project the FLEXPART grid
f_grid 		= 'FLEXPART_grid.h5'
base_path 	= '/Volumes/storage/FLEXPART/Alert_2016/FLEXPART_2016_dkunkel/'
p_grid    	= os.path.join(base_path,f_grid)
xlon_i = PES.get_var(p_grid, 'xlon')
xlat_i = PES.get_var(p_grid, 'xlat')
x,y=m(xlon_i,xlat_i)

#draw the map details
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = 'w', zorder = 0)
m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#make the PES contour plot 
levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
cols=PES.makeColormap(color_list)
norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
cs = m.contourf(x,y,avgd_PES, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

#add a scale bar
#cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
cbar.set_label('FLEXPART-WRF residence time (s)')


os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/')
plt.savefig('FLEXPART_avgdPES_0-100m_Alert2016_' + desc + '.png', bbox_inches='tight', dpi=300)
plt.show()

#20160311-1757 20160312-2009 20160313-1749 20160314-1521 20160315-1510 20160316-1529 20160317-1658 20160318-1507 20160319-1801 20160320-1750 20160321-1447 20160322-1444 20160323-1556 20160324-1453 20160326-1726 20160327-1745 20160328-1455 

