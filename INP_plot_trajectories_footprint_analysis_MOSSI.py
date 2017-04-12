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
from matplotlib.path import Path
import pickle

bt_length 				= 20

include_trajectories	= True

include_arctic_circle 	= True

include_oceans			= True
ocean_grid_spacing 		= 0.5
ocean_grid_file			= '/Users/mcallister/projects/INP/ocean grids/ocean_grid_05x05.pckl'
plot_ocean_grid 		= False


include_fires			= False
fire_threshold			= 80.
MODIS_file				= 'fire_archive_M6_8493-MOSSI2014.txt'


include_sea_ice			= True
max_ice_day				= 185 				#MOSSI 2016 max is 185 for 20d 195 for 10d, 2014 max is 175 for 20d 185 for 10d

include_deserts 		= False

boundary_layer			= True

save_fig				= False

nx, ny 					= 180.,90. 				#grid
grid_size				= 360/nx,180/ny			#degrees
radius_earth			= 6371200.0
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

		if sample_date != datetime(2014,7,18):
			continue

		julian_sample_date = sample_date.timetuple().tm_yday
		print newline[0], start_time, end_time, julian_sample_date 

		m=Basemap(width=9000000., height=9000000., projection='stere',ellps='WGS84', lon_0=270., lat_0=90., lat_ts=60.,resolution='i')


		fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
		m.drawcoastlines()
		#m.drawcountries()
		parallels = np.arange(0.,90,10.)
		#m.drawparallels(parallels,labels=[False,True,False,False])
		meridians = np.arange(10.,351.,20.)
		#m.drawmeridians(meridians,labels=[False,False,False,True])


		#### trajectory heatmap
		#get gridded data
		endpoints = INPmod.parseMOSSITrajectories(traj_file_location,start_time,end_time,boundary_layer,bt_length)
		total_endpoints = len(endpoints)
		np_endpoints = np.array(endpoints)
		lats = np_endpoints[:,0] 
		lons = np_endpoints[:,1]
		heights = np_endpoints[:,2]
		xs,ys,density_trajs,max_density,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats,lons,m)

		#make colormap and color bar
		my_cmap = INPmod.makeColormap('#e6f0ff','#005ce6','#001f4d',max_density)
		tick_pts = range(1,int(max_density),int(max_density/5))
		tick_labels = []
		for pt in tick_pts:
			label = round(pt*1.0/len(endpoints),3)
			tick_labels.append(label)


		if include_trajectories == True:
			##do plotting
			mesh1 = m.pcolormesh(xs, ys, density_trajs,vmin=0.01,cmap = my_cmap)#,edgecolor = None)
			cb1 = plt.colorbar(mesh1,ticks=tick_pts,orientation='horizontal')
			cb1.set_label('fraction of time in grid cell')
			cb1.ax.set_xticklabels(tick_labels)  # horizontal colorbar
			
			#####overlay the scatter points to see that the density is working as expected
			#x,y = m(lons, lats)
			#bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),vmin = 0, vmax = 8000, edgecolors='none', marker = 'o',s=6)#,norm=matplotlib.colors.LogNorm())
			#cb1 = plt.colorbar(bt,orientation='horizontal')
			#cb1.set_label('altitude (m)')


		#### add fires
		patches = []
		hours_fires_n =0
		if include_fires == True:
			MODIS_fires = INPmod.getMODISFires(sample_date,fire_threshold,bt_length,MODIS_file)
			print len(MODIS_fires), 'fires'
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

			#### calc overlap for fires and enpoints
			#plot a density map of fire points that is on the same grid as the endpoints
			#multiply the values of each cell, if no enpoints or fires value is 0, else value is #hours x #fires in units of hours
			lats_f = [row[1] for row in MODIS_fires]
			lons_f = [row[2] for row in MODIS_fires]
			xs2,ys2,density_fires,max_density2,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats_f,lons_f,m)
			
			#zip together the density maps for the fires and endpoints
			fire_overlap = [a*b for a,b in zip(density_trajs,density_fires)]
			hours_fires_n = np.sum(fire_overlap)/total_endpoints
			print 'hours*fires ',hours_fires_n
			


		#### add deserts
		desert_hours_n = 0
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
		sea_ice_overall_fraction = 0
		if include_sea_ice == True:
			#calc overlap for sea ice and enpoints
			#plot a density map of sea ice points that is on the same grid as the endpoints
			sea_ice, snow, sea_ice_pts = INPmod.getSeaIceAndSnow(m, start_time.year, julian_sample_date-bt_length)
			lons_si = [row[0] for row in sea_ice_pts]
			lats_si = [row[1] for row in sea_ice_pts]  
			xs_si,ys_si,density_si,max_density_si,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats_si,lons_si,m)
			#mesh1 = m.pcolormesh(xs, ys, density_si,vmin=6,cmap = my_cmap, alpha=1)
			#combine sea ice and trajectory density arrrays and check seaice value.  If seaice value >6 record the number of endpoints (#use 6 b/c of high resolution comapred to ocean data and issues with land overlap).
			sea_ice_fractions = []
			sea_ice_overlap_pts = []
			i=0
			for row in np.dstack((density_trajs,density_si)):
				j=0
				for endp_number,si_pts in row:
					if endp_number >0 :    
						sea_ice_area = 4000*4000.*si_pts#23684.997*23684.997*si_pts #m2
						ll_lon = lon_bins[0][j]
						ll_lat = lat_bins[i][0]
						ll_lr_distance = INPmod.haversine(ll_lon, ll_lat, (ll_lon + grid_size[0]), ll_lat,radius_earth)
						ll_ul_distance = INPmod.haversine(ll_lon, ll_lat, ll_lon, (ll_lat + grid_size[1]),radius_earth)
						ul_ur_distance = INPmod.haversine(ll_lon, (ll_lat + grid_size[1]), (ll_lon + grid_size[0]), (ll_lat + grid_size[1]),radius_earth)
						grid_cell_area = (ul_ur_distance + ll_lr_distance)*ll_ul_distance/2 #Area of a trapezoid=(a+b)*h/2
						print ll_lon,ll_lat,si_pts,sea_ice_area,grid_cell_area,sea_ice_area/grid_cell_area
						sea_ice_fractions.append(sea_ice_area*endp_number/grid_cell_area)
						sea_ice_overlap_pts.append([ll_lon+grid_size[0]/2,ll_lat+grid_size[1]/2,(sea_ice_area/grid_cell_area)])  #centered
					j+=1
				i+=1
			
			sea_ice_overall_fraction = 	np.sum(sea_ice_fractions)/total_endpoints
			#patches for plotting
			si_patch_coll = PatchCollection(sea_ice,facecolor='#ffcc00',edgecolor='#ffcc00', alpha = .1)

			sea_ice_patches = axes.add_collection(si_patch_coll)
			#plt_x,plt_y = m(lons_si,lats_si)
			#si = m.scatter(plt_x,plt_y)
			#sn_patch_coll = PatchCollection(snow,facecolor='white',edgecolor='white', alpha = 0.3)
			#snow_patches = axes.add_collection(sn_patch_coll)
			
			##for plotting si fraction
			#for row in sea_ice_overlap_pts:
			#	lons_io    = row[0]
			#	lats_io    = row[1]
			#	fraction_io  = row[2]
			#	lono,lato = m(lons_io, lats_io)
			#	fraction  = plt.text(lono,lato, str(round(fraction_io,2)), color='r', fontsize=12)


		#### add oceans
		if include_oceans == True:
			overlap_ocean_grid = []
			#### calc overlap for ocean and enpoints
			#plot a density map of ocean points that is on the same grid as the endpoints
			ocean_pts = pickle.load(open(ocean_grid_file, 'rb' ))
			lons_o = [ocean_pt[0] for ocean_pt in ocean_pts]
			lats_o = [ocean_pt[1] for ocean_pt in ocean_pts]
			xs_o,ys_o,density_op,max_density_op,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats_o,lons_o,m)
			
			#zip together the density maps for the fires and endpoints
			ocean_fraction_list = []
			ocean_overlap_pts = []
			i=0
			for row in np.dstack([density_trajs,density_op]):
				j=0
				for endp_number,ocean_number in row:
					if endp_number > 0:
						ll_lon = lon_bins[0][j]
						ll_lat = lat_bins[i][0]
						ocean_fraction = ocean_number/((2./ocean_grid_spacing))**2
						ocean_endpoint_factor = ocean_fraction*endp_number
						ocean_fraction_list.append(ocean_endpoint_factor)

						#for plotting
						if plot_ocean_grid == True:
							if ocean_number >0:
								ocean_overlap_pts.append([ll_lon+grid_size[0]/2,ll_lat+grid_size[1]/2,ocean_fraction])  #centered
								overlap_ocean_grid = INPmod.getOceanGridForOverlap(ocean_pts,ll_lon,ll_lat,grid_size,overlap_ocean_grid)
					j+=1
				i+=1
			
			#####overlay the scatter points and desnity grid to see that the density is working as expected
			#mesh1 = m.pcolormesh(xs_o,ys_o, density_op,vmin=1,vmax=20,cmap = my_cmap)
			if plot_ocean_grid == True:
				lons_og = [row[0] for row in overlap_ocean_grid]
				lats_og = [row[1] for row in overlap_ocean_grid]
				lonog,latog = m(lons_og, lats_og)
				oog = m.scatter(lonog,latog, color = 'grey')

				for row in ocean_overlap_pts:
					lons_o    = row[0]
					lats_o    = row[1]
					fraction  = row[2]
					lono,lato = m(lons_o, lats_o)
					fraction  = plt.text(lono,lato, str(round(fraction,2)), color='r', fontsize=12)
					#bt = m.scatter(lono,lato)
			

			ocean_overall_fraction = np.sum(ocean_fraction_list)/total_endpoints
			print ocean_overall_fraction, sea_ice_overall_fraction, ocean_overall_fraction - sea_ice_overall_fraction



		#### add arctic circle
		if include_arctic_circle == True:
			arctic_circle = []
			for lon in range(0,361,1):
				ac_endpoint = [66.55, lon]
				arctic_circle.append(ac_endpoint)
			ac_endpoints = np.array(arctic_circle)
			ac_lats = ac_endpoints[:,0] 
			ac_lons = ac_endpoints[:,1]
			x,y = m(ac_lons,ac_lats)
			ac = m.plot(x,y, color = 'k', linewidth = 2.5,)
			
		plt.show()
		sys.exit()

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
