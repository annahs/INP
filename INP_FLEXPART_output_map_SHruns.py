#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
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


p_data          = '/Users/mcallister/projects/flexpart/INP1_20140714/Output/FNL/summedPES.h5'
p_trajectory    = '/Users/mcallister/projects/flexpart/INP1_20140714/Output/FNL/trajectories.txt'
p_ncfile        = '/Users/mcallister/projects/flexpart/INP1_20140714/Output/FNL/grid_time_20140714130200.nc'


#define the figure
fig = plt.figure(figsize=(10,10))

#get the grid information
xlat_l = PES.get_var(p_ncfile, 'latitude')
xlon_l = PES.get_var(p_ncfile, 'longitude')


xlon,xlat = np.meshgrid(xlon_l,xlat_l)


#get the previously summed PES information
Conc_var = PES.get_var(p_data, 'Conc_pCol300') #Conc_tCol Conc_pCol300
                       
#create a basemap instance
m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)

#re-project the FLEXPART grid
x,y=m(xlon,xlat)

#draw the map details
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = 'w', zorder = 0)
m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#make the PES contour plot 
#levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
levels = ([0.001,0.01,0.1,1.,10.,50,100.,500.,1000.,5000,10000,20000,50000])
color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
cols=PES.makeColormap(color_list)
norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
cs = m.contourf(x,y,Conc_var, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

#add a scale bar
#cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
cbar.set_label('FLEXPART-WRF total column residence time (s)')


params = {'mathtext.default': 'regular' }          
plt.rcParams.update(params)
traj_days = PES.getDaysOnTrajectory(p_trajectory, [1,2,3,4,5,6,7])
print traj_days
for day in traj_days:
    lat = day[0] 
    lon = day[1] 
    day = day[2] 
    xd,yd = m(lon,lat)
    db = m.plot(xd,yd,marker = 's',markerfacecolor='w',markersize=14)
    db = m.scatter(xd,yd,marker = r'${}$'.format(int(day)),zorder = 100,s=80)



xs,ys = m(-61.08522,67.24028167)
m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)

os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/')
plt.savefig('FLEXPART-FNL_PES_0-300m_20140714-1302_AmundsenINP_alts.png', bbox_inches='tight', dpi=300)
plt.show()
