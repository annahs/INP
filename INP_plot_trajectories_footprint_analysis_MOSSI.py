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

include_oceans			= True

include_fires			= True
fire_threshold			= 80.
MODIS_file				= 'fire_archive_M6_8493-MOSSI2014.txt'


include_sea_ice			= True
max_ice_day				= 185 				#MOSSI 2016 max is 185 for 20d 195 for 10d, 2014 max is 175 for 20d 185 for 10d

include_deserts 		= True

boundary_layer			= True

save_fig				= True

nx, ny 					= 180,90. 				#grid

mossi_file = '/Users/mcallister/projects/INP/MOSSI/MOSSI_sampling_start_stop_times_2014.txt' 


#set up parameters text file
p_file = '/Users/mcallister/projects/INP/MOSSI/AmundsenINP_2014_footprint_parameters-' + str(bt_length) +  'd.txt'
#delete if the file exists
try:
    os.remove(p_file)
except OSError:
    pass
with open(p_file,'w') as pf:
	pf.write('sample_start_time' + '\t' + 'sample_end_time' + '\t' + 'fire_parameter' + '\t' + 'desert_parameter' + '\t' + 'open_water_parameter' + '\t' + 'sea_ice_parameter' + '\n' )

traj_file_location = '/Users/mcallister/projects/INP/MOSSI/trajectories'
i=0
with open(mossi_file,'r') as f:
	f.readline()
	for line in f:
		newline = line.split()
		sample_no = newline[0]
		start_time 	= parser.parse(newline[1] + '-'+ newline[2])
		end_time	= parser.parse(newline[3] + '-'+ newline[4])
		
		#### set up the basemap instance  	
		sample_date = datetime(start_time.year,start_time.month,start_time.day)
		julian_sample_date = sample_date.timetuple().tm_yday
		print newline[0], start_time, end_time, julian_sample_date 
		#m = Basemap(width=15000000,height=11000000,
		#            rsphere=(6378137.00,6356752.3142),\
		#            resolution='l',area_thresh=1000.,projection='lcc',\
		#            lat_1=45.,lat_2=55,lat_0=50,lon_0=140.)
		m = Basemap(projection='npstere',boundinglat=40,lon_0=270,resolution='l')

		fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
		m.drawcoastlines()
		#m.drawcountries()
		parallels = np.arange(0.,90,10.)
		m.drawparallels(parallels,labels=[False,True,False,False])
		meridians = np.arange(10.,351.,20.)
		m.drawmeridians(meridians,labels=[False,False,False,True])


		#### trajectory heatmap
		#get gridded data
		endpoints = INPmod.parseMOSSITrajectories(traj_file_location,start_time,end_time,boundary_layer,bt_length)
		total_endpoints = len(endpoints)
		np_endpoints = np.array(endpoints)
		lats = np_endpoints[:,0] 
		lons = np_endpoints[:,1]
		heights = np_endpoints[:,2]
		xs,ys,density_trajs,max_density = INPmod.getGriddedData(nx,ny,lats,lons,m)

		#make colormap and color bar
		my_cmap = INPmod.makeColormap('#e6f0ff','#005ce6','#001f4d',max_density)
		tick_pts = range(1,int(max_density),int(max_density/5))
		tick_labels = []
		for pt in tick_pts:
			label = round(pt*1.0/len(endpoints),3)
			tick_labels.append(label)


		if include_trajectories == True:
			##do plotting
			mesh1 = m.pcolormesh(xs, ys, density_trajs,vmin=0.01,cmap = my_cmap)
			cb1 = plt.colorbar(mesh1,ticks=tick_pts,orientation='horizontal')
			cb1.set_label('fraction of time in grid cell')
			cb1.ax.set_xticklabels(tick_labels)  # horizontal colorbar
			
			###overlay the scatter points to see that the density is working as expected
			#x,y = m(lons, lats)
			#bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),vmin = 0, vmax = 8000, edgecolors='none', marker = 'o',s=6)#,norm=matplotlib.colors.LogNorm())
			#cb1 = plt.colorbar(bt,orientation='horizontal')
			#cb1.set_label('altitude (m)')


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

			#### calc overlap for fires and enpoints
			#plot a density map of fire points that is on the same grid as the endpoints
			#multiply the values of each cell, if no enpoints or fires value is 0, else value is #hours x #fires in units of hours
			lats_f = [row[1] for row in MODIS_fires]
			lons_f = [row[2] for row in MODIS_fires]
			xs2,ys2,density_fires,max_density2 = INPmod.getGriddedData(nx,ny,lats_f,lons_f,m)
			
			#zip together the density maps for the fires and endpoints
			fire_overlap = [a*b for a,b in zip(density_trajs,density_fires)]
			hours_fires_n = np.sum(fire_overlap)/total_endpoints
			print 'hours*fires ',hours_fires_n
			patch_coll = PatchCollection(patches,facecolor = '#ff531a',edgecolor='#ff531a')
			fire_patches = axes.add_collection(patch_coll)


		#### add deserts
		if include_deserts == True:
			# create a list of possible coordinates
			g = xs, ys
			coords = list(zip(*(c.flat for c in g)))
			plot_pts=[]
			endpoint_counts = []
			desert_names, desert_patches = INPmod.getDesertShapes(m)
			patch_coll_d = PatchCollection(desert_patches,facecolor = '#bf8040',edgecolor='#362D0C',alpha = 0.15)
			for patch in desert_patches:
				for coord in coords:
					if patch.contains_point(coord, radius=0): 
						index = np.where(xs == coord[0])
						endpoint_count = density_trajs[index]
						endpoint_counts.append(endpoint_count[0])
						plot_pts.append(coord)

			deserts = axes.add_collection(patch_coll_d)
			#pprint(desert_names)
			tx = [row[0] for row in plot_pts]
			ty = [row[1] for row in plot_pts]
			#tests = m.scatter(tx,ty, color = 'orange')
			desert_hours_n = np.sum(endpoint_counts)/total_endpoints
			print 'desert hours ', desert_hours_n



		#### add sea ice and snow
		if include_sea_ice == True:
			sea_ice_hours = 0
			#count all enpoints north of 86deg. This is always frozen, but sea ice point density is low due to converging longitude lines
			for endpoint_lat in lats:
				if endpoint_lat > 86:
					sea_ice_hours += 1

			#calc overlap for sea ice and enpoints
			#plot a density map of sea ice points that is on the same grid as the endpoints
			sea_ice, snow, sea_ice_pts = INPmod.getSeaIceAndSnow(m, start_time.year, julian_sample_date-bt_length)
			lats_si = [row[1] for row in sea_ice_pts]  
			lons_si = [row[0] for row in sea_ice_pts]
			xs_si,ys_si,density_si,max_density_si = INPmod.getGriddedData(nx,ny,lats_si,lons_si,m)
			#mesh1 = m.pcolormesh(xs, ys, density_si,vmin=6,cmap = my_cmap, alpha=1)

			#combine sea ice and trajectory density arrrays and check seaice value.  If seaice value >6 record the number of endpoints (#use 6 b/c of high resolution comapred to ocean data and issues with land overlap).
			for row in np.dstack((density_trajs,density_si)):
				for traj_hours,si_pts in row:
					if si_pts > 6 and traj_hours >0 :    
						sea_ice_hours += traj_hours
			sea_ice_hours_n = sea_ice_hours/total_endpoints
			print 'sea ice hours ',sea_ice_hours_n
			
			#patches for plotting
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


		#### add oceans
		if include_oceans == True:
			ocean_hours = 0
			test = []
			for row in np.dstack((xs, ys)):
				for xpt,ypt in row:
					#for some reason is_land() == False is screwed up by the poles, so we'll restrict our search area a bit
					lonpt, latpt = m(xpt,ypt,inverse=True)
					if (-90 < latpt < 89.9):   
						if m.is_land(xpt, ypt) == False:
							x_index,y_index = INPmod.find_index_of_nearest_xy(xs,ys,xpt,ypt)
							o_endpoint_count = density_trajs[x_index][y_index]
							if o_endpoint_count > 0:
								test.append([xpt,ypt])
							ocean_hours += o_endpoint_count

			txo = [row[0] for row in test]
			tyo = [row[1] for row in test]
			#tests = m.scatter(txo,tyo)
			open_water_hours_n = (ocean_hours-sea_ice_hours)/total_endpoints

			print 'ocean hours ',ocean_hours, ocean_hours/total_endpoints
			try:
				print 'open water hours ',open_water_hours_n
			except:
				print 'no sea ice'



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
			

		##save parameters
		p_line = [start_time, end_time,round(hours_fires_n,4), round(desert_hours_n,4), round(open_water_hours_n,4), round(sea_ice_hours_n,4)]
		with open(p_file,'a') as pf:
			line = '\t'.join(str(x) for x in p_line)
			pf.write(line + '\n')


		#### add text
		description = str(start_time.year)+'-'+str(start_time.month).zfill(2)+'-'+str(start_time.day).zfill(2)+ ' '+ str(start_time.hour).zfill(2) + ':'+ str(start_time.minute).zfill(2) + '-' +str(bt_length) + 'day back-trajectories'
		bl = ''
		if boundary_layer == True:
				bl = '_inPBL'
		plt.text(0.0, 1.025,'Sample starting at: ' + description, fontsize = 14,transform=axes.transAxes)

		#### save
		os.chdir('/Users/mcallister/projects/INP/MOSSI/footprint analysis 2014/')

		if save_fig == True:
			plt.savefig('sample' + sample_no + '_' + str(start_time.year)+'-'+str(start_time.month).zfill(2)+'-'+str(start_time.day).zfill(2) + '-' + str(start_time.hour).zfill(2) + str(start_time.minute).zfill(2)  + '_' + str(bt_length) +'day_back-trajectories'+ bl+ '_footprint.pdf',format = 'pdf', bbox_inches='tight') 
		else:
			plt.show()
		plt.close()
		i+=1
