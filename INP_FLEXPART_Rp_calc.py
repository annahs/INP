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
import numpy.ma as ma
import Alert_sampling_times as AL


sample_type 			= 'MD' #INP25 MD SS
designated_samples		= True
sample_numbers			= [1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
#or
case 					= 'highest'
number 					= 4
#
Rp_plot					= False
footprint_layer_height 	= 100
days_back				= 20



#for sample_type in ['INP25', 'MD']:
#	for case in ['lowest','highest']:

if designated_samples == True:
	sample_times  = AL.getSamples(sample_type,sample_numbers)
	descr = sample_type + '_0-'+ str(footprint_layer_height) + 'm - samples ' + str(sample_numbers) + '-' + str(days_back) + 'days back '
else:
	sample_times  = AL.getHours(sample_type,case,number_samples=number)
	sample_numbers = number
	descr = sample_type + case + '_' + str(sample_numbers) + ' samples - ' +  sample_type + '_0-'+ str(footprint_layer_height) + 'm - ' + str(days_back) + 'days back '

all_times     = AL.getHours(sample_type,'all')

f_grid 		= 'FLEXPART_grid.h5'
base_path 	= '/Volumes/storage/FLEXPART/Alert_2016/FLEXPART_2016_dkunkel/'
p_grid    	= os.path.join(base_path,f_grid)
sp,sp_sim_count  = INP.getAveragedAlert2016PES(sample_times,footprint_layer_height,days_back) 
st,st_sim_count  = INP.getAveragedAlert2016PES(all_times,footprint_layer_height,days_back) 
stm = ma.masked_less(st, 0.005)

print sample_type,case
print sp_sim_count, st_sim_count
pprint(sample_times)

xlon_i = PES.get_var(p_grid, 'xlon')
xlat_i = PES.get_var(p_grid, 'xlat')

Rp_PES = np.divide(sp,stm)*(sp_sim_count*1.0/st_sim_count)

Rp_min = np.nanmin(Rp_PES)
Rp_max = np.nanmax(Rp_PES)
print Rp_min, Rp_max

###plots
#define the figure
fig = plt.figure(figsize=(10,10))

#create a basemap instance
m = Basemap(width=12000000,height=12000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.)

#re-project the FLEXPART grid
x,y=m(xlon_i,xlat_i)

#draw the map details
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = 'w', zorder = 0)
m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])


os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/')

#make the Rp contour plot 
if Rp_plot == True:
	levels = np.arange(0,1.1,0.1)
	#color_list = ['#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819']
	color_list = ['w','#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']
	cols=PES.makeColormap(color_list)
	norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
	cs = m.contourf(x,y,Rp_PES, levels=levels, cmap=cols,  norm=norm) 

	#add a color bar
	cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
	cbar.set_label('Ratio')
	xs,ys = m(-62.382840,82.500401)
	m.scatter(xs,ys,marker = '*',zorder = 100, color = 'r', s=275)
	plt.savefig('Rp_' + descr + '.png', bbox_inches='tight', dpi=300)

#make avgdPES contour plot
else:
	levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
	color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
	cols=PES.makeColormap(color_list)
	norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
	cs = m.contourf(x,y,sp, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

	#add a color bar
	cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
	#cbar.set_label('FLEXPART Residence Time (s) - footprint layer (0-'+ str(footprint_layer_height) + 'm) - ' + sample_type)
	cbar.set_label('FLEXPART Residence Time (s)')

	xs,ys = m(-62.382840,82.500401)
	m.scatter(xs,ys,marker = '*',zorder = 100, color = 'r', s=275)
	plt.savefig('avgd_FLEXPART_PES_' + descr + '.png', bbox_inches='tight', dpi=300)



plt.show()


