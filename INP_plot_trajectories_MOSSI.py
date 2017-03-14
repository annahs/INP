#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import os
import sys
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
from dateutil import parser
import math
from matplotlib.colors import LinearSegmentedColormap
import INP_source_apportionment_module as INPmod


bt_length 				= 10

include_trajectories	= True

include_arctic_circle 	= True

include_fires			= True
fire_threshold			= 80.
MODIS_file				= 'fire_archive_M6_8473.txt'

include_sea_ice			= True
max_ice_day				= 236 				#Inuvik 103 (april 13)  Eureka 91 (April 1)  Alert 91 (April 1)

include_deserts 		= True

boundary_layer			= False

save_fig				= True

traj_type 				= 'met_ensemble'		#'posn_matrix' 'met_ensemble'
nx, ny 					= 180,90. 				#grid
mossi_file = '/Users/mcallister/projects/INP/MOSSI/MOSSI_sampling_start_stop_times_b.txt'


i=0
with open(mossi_file,'r') as f:
	f.readline()
	for line in f:
		newline = line.split()
		sample_no = newline[0]
		start_time 	= parser.parse(newline[1] + '-'+ newline[2])
		end_time	= parser.parse(newline[3] + '-'+ newline[4])
		print newline[0], start_time, end_time
		file_location = '/Users/mcallister/projects/INP/MOSSI/trajectories'
		sample_date = datetime(start_time.year,start_time.month,start_time.day)

		m = Basemap(projection='npstere',boundinglat=40,lon_0=270,resolution='l')
		fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
		m.drawcoastlines()
		#m.drawcountries()
		parallels = np.arange(0.,90,10.)
		m.drawparallels(parallels,labels=[False,True,False,False])
		meridians = np.arange(10.,351.,20.)
		m.drawmeridians(meridians,labels=[False,False,False,True])


		#### trajectories
		endpoints = INPmod.parseMOSSITrajectories(file_location,start_time,end_time,boundary_layer,bt_length)
		total_endpoints = len(endpoints)
		np_endpoints = np.array(endpoints)
		lats = np_endpoints[:,0] 
		lons = np_endpoints[:,1]
		heights = np_endpoints[:,2]


		if include_trajectories == True:
			x,y = m(lons, lats)
			bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),vmin = 0, vmax = 8000, edgecolors='none', marker = 'o',s=6)#,norm=matplotlib.colors.LogNorm())
			cb1 = plt.colorbar(bt,orientation='horizontal')
			cb1.set_label('altitude (m)')


		#### add fires
		patches = []
		if include_fires == True:
			MODIS_fires = INPmod.getMODISFires(sample_date,fire_threshold,bt_length,MODIS_file)

			for fire in MODIS_fires:
				acq_date_time 	= fire[0]
				lat 			= fire[1]
				lon 			= fire[2]
				scan 			= fire[3]
				track 			= fire[4]
				x,y = m(lon,lat)
				#fires = m.scatter(x,y, s = 6, color = 'r')

				x1,y1 = (x-500*scan),(y-500*track)
				x2,y2 = (x-500*scan),(y+500*track)
				x3,y3 = (x+500*scan),(y+500*track)	
				x4,y4 = (x+500*scan),(y-500*track)
				p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)]) 
				#axes.add_patch(p)
				patches.append(p)

			patch_coll = PatchCollection(patches,facecolor = '#ff531a',edgecolor='#ff531a')
			fire_patches = axes.add_collection(patch_coll)


		#### add deserts
		if include_deserts == True:
			desert_names, desert_patches = INPmod.getDesertShapes(m)
			patch_coll_d = PatchCollection(desert_patches,facecolor = '#bf8040',edgecolor='#362D0C',alpha = 0.15)
			deserts = axes.add_collection(patch_coll_d)
			
		#### add sea ice and snow
		if include_sea_ice == True:
			sea_ice, snow, sea_ice_pts = INPmod.getSeaIceAndSnow(m, start_time.year, max_ice_day)
			si_patch_coll = PatchCollection(sea_ice,facecolor='#ffcc00',edgecolor='#ffcc00', alpha = 0.05)
			sea_ice_patches = axes.add_collection(si_patch_coll)
			#sn_patch_coll = PatchCollection(snow,facecolor='white',edgecolor='white', alpha = 0.3)
			#snow_patches = axes.add_collection(sn_patch_coll)
				
			##plot markers as a check on density plot
			#for sea_ice_pt in sea_ice_pts:
			#	lon 			= sea_ice_pt[0]
			#	lat 			= sea_ice_pt[1]
			#	x,y = m(lon,lat)
			#	sea_ice_markers = m.scatter(x,y,color = 'r')



		#### add arctic circle
		if include_arctic_circle == True:
			arctic_circle = []
			for lon in range(0,360,1):
				ac_endpoint = [66.55, lon]
				arctic_circle.append(ac_endpoint)
			ac_endpoints = np.array(arctic_circle)
			ac_lats = ac_endpoints[:,0] 
			ac_lons = ac_endpoints[:,1]
			x,y = m(ac_lons,ac_lats)
			ac = m.plot(x,y, color = 'k', linewidth = 2.5,)
			

		#### add text
		description = str(start_time.year)+'-'+str(start_time.month).zfill(2)+'-'+str(start_time.day).zfill(2)+ ' '+ str(start_time.hour).zfill(2) + ':'+ str(start_time.minute).zfill(2) + '-' +str(bt_length) + 'day back-trajectories'
		plt.text(0.0, 1.025,'Sample starting at: ' + description, fontsize = 14,transform=axes.transAxes)

		#### save
		os.chdir('/Users/mcallister/projects/INP/MOSSI/footprint analysis/')

		if save_fig == True:
			plt.savefig('sample' + sample_no + '_' + str(start_time.year)+'-'+str(start_time.month).zfill(2)+'-'+str(start_time.day).zfill(2) + '-' + str(start_time.hour).zfill(2) + str(start_time.minute).zfill(2)  + '_' + str(bt_length) +'day_back-trajectories_trajectories.pdf',format = 'pdf', bbox_inches='tight') 

		#plt.show()
		plt.close()
		i+=1
