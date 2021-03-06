import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import os
import sys
import matplotlib.colors
import colorsys
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import pickle
import mmap



timezone = timedelta(hours = 1)

endpointsALERT =  {}

dir = '/Users/mcallister/projects/Alert_INP2016/bin/working'
os.chdir(dir)

clusters = []
cluster_no = 1	
for file in os.listdir('.'):
	if file.endswith('3mean.tdump'):
		
		tdump_file = open(file, 'r')
		print file
		endpoints = []
		data_start = False
	
		
		for line in tdump_file:
			newline = line.split()
			
			
			
			if data_start == True:
				lat = float(newline[9])
				lon = float(newline[10])
				height = float(newline[11])
				#pressure = float(newline[11]) #in hPa
				year =  int(newline[2])
				month = int(newline[3])
				day = int(newline[4])
				hour = int(newline[5])
				Py_datetime_UTC = datetime(year, month, day, hour)
				Py_datetime = Py_datetime_UTC + timezone
				
				endpoint = [lat, lon,height]
				endpoints.append(endpoint)
				
			if newline[1] == 'PRESSURE':
				data_start = True
		
		tdump_file.close() 
		
		endpointsALERT[cluster_no]=endpoints
		clusters.append(cluster_no)
		cluster_no +=1
		

		
		

#plottting
###set up the basemap instance  
lat_pt = 82.
lon_pt = -62.

m = Basemap(projection='nplaea',boundinglat=35,lon_0=270,resolution='l')

#m = Basemap(width=3300000,height=3300000,
#			rsphere=(6378137.00,6356752.3142),
#			resolution='l',area_thresh=1000.,projection='lcc',
#			lat_1=47.,lat_2=55,lat_0=lat_pt,lon_0=lon_pt)
	
	
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)
#m.drawmapboundary(fill_color='white') 
#
##rough shapes 
m.drawcoastlines()
#m.fillcontinents(color='#FFFFBF',lake_color='#ABD9E9',zorder=0)
m.drawcountries()

m.bluemarble()

####other data


##draw map scale
#scale_lat = lat_pt-7
#scale_lon = lon_pt-6
#m.drawmapscale(scale_lon, scale_lat, -118, 32, 100, barstyle='simple', units='km', fontsize=9, yoffset=None, labelstyle='simple', fontcolor='k', fillcolor1='w', fillcolor2='k', ax=None, format='%d', zorder=None)
parallels = np.arange(0.,81,10.)
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[False,False,False,True])



linewidth = 2.5
pre_linewidth = 2
alphaval = 1

S = 1.0#0.1
hue = 0#0.65
i=0



colors = ['b','orange','g','r','c','m','k','y','#DF7401','#585858','grey','#663300']
#labels = ['','','','','','', '','']
for cluster_no in clusters:
	print cluster_no,colors[cluster_no]
	np_endpoints = np.array(endpointsALERT[cluster_no])
	lats = np_endpoints[:,0] 
	lons = np_endpoints[:,1]
	heights = np_endpoints[:,2]
	x,y = m(lons,lats)
	#bt = m.scatter(x,y, c=pressure, cmap=plt.get_cmap('jet'),edgecolors='none')
	bt = m.plot(x,y,linewidth = linewidth, color =colors[cluster_no])#, label = labels[cluster_no])
	#bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),edgecolors='none', marker = 'o')
	i+=1
	
#cb = plt.colorbar()
#cb.set_label('height (m)', rotation=270)

plt.legend(loc = 3)
dir = '/Users/mcallister/projects/Alert_INP2016/bin/SSI_clusters/'
os.chdir(dir)

plt.savefig('ALERT_HYSPLIT_cluster_means_240hr_backtrajectories-3clusters-Alert_SSI_March_2016.png', bbox_inches='tight') 
plt.show()




