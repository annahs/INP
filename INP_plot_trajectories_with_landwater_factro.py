#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import os
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
from dateutil import parser
import math
from matplotlib.colors import LinearSegmentedColormap
import INP_source_apportionment_module as INPmod
from matplotlib.collections import LineCollection


Ucluelet_path   = '/Users/mcallister/projects/INP/trajectories/Ucluelet_2013-3d/Ucluelet_2013-3d-150magl/'
Labrador_path   = '/Users/mcallister/projects/INP/trajectories/LabradorSea_2014-3d/LabradorSea_2014-3d-150magl/'
Lancaster_path  = '/Users/mcallister/projects/INP/trajectories/LancasterSound_2014-3d/LancasterSound_2014-3d-150magl/'

os.chdir(Lancaster_path)

#m = Basemap(width=1500000,height=1100000,
#		            rsphere=(6378137.00,6356752.3142),\
#		            resolution='l',area_thresh=1000.,projection='lcc',\
#		            lat_1=45.,lat_2=55,lat_0=50,lon_0=140.)

m = Basemap(width=8500000,height=6000000, resolution='l',projection='stere',lat_0=60,lon_0=-100.)

fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
m.drawcoastlines()
#m.drawcountries()
parallels = np.arange(0.,90,10.)
m.drawparallels(parallels,labels=[False,True,False,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[False,False,False,True])


land_factor		= 0
ocean_factor 	= 0
endpoints = []
for file in os.listdir('.'):
	
	if file.startswith('Untitled'):
		print file

		tdump_file = open(file, 'r')
		data_start = False
		file_trajectories = {}
		for line in tdump_file:
			newline = line.split()
			if data_start == True:
				hours_along = float(newline[8])
				lat 		= float(newline[9])
				lon 		= float(newline[10])
				height 		= float(newline[11]) 
				endpoint 	= [lat, lon, height]
				endpoints.append(endpoint)

				#xpt, ypt = m(lon, lat)
				#if m.is_land(xpt, ypt):
				#	land_factor += 1
				#else:
				#	ocean_factor += 1

			if newline[1] == 'PRESSURE':
				data_start = True
			
		tdump_file.close() 

os.chdir(Ucluelet_path)
for file in os.listdir('.'):
	
	if file.startswith('Untitled'):
		print file

		tdump_file = open(file, 'r')
		data_start = False
		file_trajectories = {}
		for line in tdump_file:
			newline = line.split()
			if data_start == True:
				hours_along = float(newline[8])
				lat 		= float(newline[9])
				lon 		= float(newline[10])
				height 		= float(newline[11]) 
				endpoint 	= [lat, lon, height]
				endpoints.append(endpoint)

		
			if newline[1] == 'PRESSURE':
				data_start = True
			
		tdump_file.close() 

os.chdir(Labrador_path)
for file in os.listdir('.'):
	
	if file.startswith('Untitled'):
		print file

		tdump_file = open(file, 'r')
		data_start = False
		file_trajectories = {}
		for line in tdump_file:
			newline = line.split()
			if data_start == True:
				hours_along = float(newline[8])
				lat 		= float(newline[9])
				lon 		= float(newline[10])
				height 		= float(newline[11]) 
				endpoint 	= [lat, lon, height]
				endpoints.append(endpoint)


			if newline[1] == 'PRESSURE':
				data_start = True
			
		tdump_file.close() 


lons = [row[1] for row in endpoints]
lats = [row[0] for row in endpoints]
hts  = [row[2] for row in endpoints]

Uc_x, Uc_y = m(-125.54, 48.92)
Lab_x, Lab_y = m(-55.61, 54.59)
Lan_x, Lan_y = m(-91.46, 74.26)

x,y = m(lons, lats)
bt = m.scatter(x,y, c=hts, cmap=plt.get_cmap('jet'), edgecolors='none', marker = '.',s=6, zorder = 10)#,norm=matplotlib.colors.LogNorm())
cb1 = plt.colorbar(bt,orientation='horizontal')
cb1.set_label('altitude (m)')

size_pt = 34
Uc_pt = m.scatter(Uc_x, Uc_y, marker='o',color='r',s=size_pt, zorder = 100)
Lab_pt = m.scatter(Lab_x, Lab_y, marker='o',color='g',s=size_pt, zorder = 100)
Lan_pt = m.scatter(Lan_x, Lan_y, marker='o',color='yellow',s=size_pt, zorder = 100)

## Create a set of line segments so that we can color them individually
## This creates the points as a N x 1 x 2 array so that we can stack points
## together easily to get the segments. The segments array for line collection
## needs to be numlines x points per line x 2 (x and y)
#points = np.array([x, y]).T.reshape(-1, 1, 2)
#segments = np.concatenate([points[:-1], points[1:]], axis=1)
#
## Create the line collection object, setting the colormapping parameters.
## Have to set the actual values used for colormapping separately.
#lc = LineCollection(segments, cmap=plt.get_cmap('jet'),
#    norm=plt.Normalize(0, 5000))
#lc.set_array(hts)
#lc.set_linewidth(3)
#
#plt.gca().add_collection(lc)



print 'land hours', land_factor 
print 'water hours', ocean_factor 
os.chdir('/Users/mcallister/projects/INP/trajectories/')
plt.savefig('LancasterSound_LabradorSea_Ucluelet-72h_backtrajectories_gdas1-150magl.png', bbox_inches='tight') 
plt.show()
