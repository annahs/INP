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

bt_length 				= 10

include_trajectories	= True
low_alt					= True #if below 250m set low_alt = True.  This will diregard "below ground" meteorology when using the trajectory ensemble

include_arctic_circle 	= True

include_sea_ice			= True

include_oceans			= True
ocean_grid_spacing 		= 0.5
ocean_grid_file			= '/Users/mcallister/projects/INP/ocean grids/ocean_grid_05x05.pckl'
plot_ocean_grid 		= False

include_deserts 		= True
desert_grid_spacing 	= 0.5
desert_grid_file		= '/Users/mcallister/projects/INP/desert grids/desert_grid_05x05.pckl'
plot_desert_grid 		= False

include_land	 		= True
land_grid_spacing 		= 0.5
land_grid_file			= '/Users/mcallister/projects/INP/land grids/land_grid_05x05.pckl'
plot_land_grid 			= False

include_fires			= True
fire_threshold			= 80.
MODIS_file				= 'fire_archive_M6_8473-MOSSI2016.txt'

boundary_layer			= True

save_fig				= True

nx, ny 					= 180.,90. 				#grid
grid_size				= 360/nx,180/ny			#degrees
radius_earth			= 6371200.0
mossi_file 				= '/Users/mcallister/projects/INP/MOSSI/MOSSI_sampling_start_stop_times_2016.txt' 







#set up parameters text file
if save_fig == True:
	p_file = '/Users/mcallister/projects/INP/MOSSI/AmundsenINP_2016_footprint_v2_parameters-' + str(bt_length) +  'd-test.txt'
	#delete if the file exists
	try:
	    os.remove(p_file)
	except OSError:
	    pass
	with open(p_file,'w') as pf:
		pf.write('sample_start_time' + '\t' + 'sample_end_time' + '\t' + 'fire_parameter' + '\t' + 'desert_parameter' + '\t' + 'open_water_parameter' + '\t' + 'sea_ice_parameter' + '\t' + 'land_parameter' + '\n' )

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

		m=Basemap(width=9000000., height=9000000., projection='stere',ellps='WGS84', lon_0=270., lat_0=90., lat_ts=60.,resolution='i',area_thresh = 5000)


		fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
		m.drawcoastlines()
		##m.drawcountries()
		#parallels = np.arange(0.,90,10.)
		#m.drawparallels(parallels,labels=[False,True,False,False])
		#meridians = np.arange(10.,351.,20.)
		#m.drawmeridians(meridians,labels=[False,False,False,True])


		#### trajectory heatmap
		#get gridded data
		endpoints = INPmod.parseMOSSITrajectories(traj_file_location,start_time,end_time,boundary_layer,bt_length,low_alt)
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
			cb1.set_label('Time spent in grid cell')
			cb1.ax.set_xticklabels(tick_labels)  # horizontal colorbar
			
			#####overlay the scatter points to see that the density is working as expected
			#x,y = m(lons, lats)
			#bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),vmin = 0, vmax = 8000, edgecolors='none', marker = 'o')#,norm=matplotlib.colors.LogNorm())
			#cb1 = plt.colorbar(bt,orientation='horizontal')
			#cb1.set_label('altitude (m)')


		#### add fires
		patches = []
		fire_parameter =0
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

				fire_pixel_halfwidth = 500
				x1,y1 = (x-fire_pixel_halfwidth*scan),(y-fire_pixel_halfwidth*track)
				x2,y2 = (x-fire_pixel_halfwidth*scan),(y+fire_pixel_halfwidth*track)
				x3,y3 = (x+fire_pixel_halfwidth*scan),(y+fire_pixel_halfwidth*track)	
				x4,y4 = (x+fire_pixel_halfwidth*scan),(y-fire_pixel_halfwidth*track)
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
			fire_parameter = np.sum(fire_overlap)/total_endpoints
			print 'fire_parameter ',fire_parameter
			


		#### add deserts
		if include_deserts == True:
			overlap_desert_grid = []
			#### calc overlap for ocean and enpoints
			#plot a density map of ocean points that is on the same grid as the endpoints
			desert_pts = pickle.load(open(desert_grid_file, 'rb' ))
			lons_d = [desert_pt[0] for desert_pt in desert_pts]
			lats_d = [desert_pt[1] for desert_pt in desert_pts]
			xs_d,ys_d,density_dp,max_density_dp,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats_d,lons_d,m)
			
			#zip together the density maps for the fires and endpoints
			desert_fraction_list = []
			desert_overlap_pts = []
			i=0
			for row in np.dstack([density_trajs,density_dp]):
				j=0
				for endp_number,desert_number in row:
					if endp_number > 0:
						ll_lon = lon_bins[0][j]
						ll_lat = lat_bins[i][0]
						desert_fraction = desert_number/((2./desert_grid_spacing))**2
						desert_endpoint_factor = desert_fraction*endp_number
						desert_fraction_list.append(desert_endpoint_factor)

						#for plotting
						if plot_desert_grid == True:
							if desert_number >0:
								desert_overlap_pts.append([ll_lon+grid_size[0]/2,ll_lat+grid_size[1]/2,desert_fraction])  #centered
								overlap_desert_grid = INPmod.getAreaGridForOverlap(desert_pts,ll_lon,ll_lat,grid_size,overlap_desert_grid)
					j+=1
				i+=1

			#####overlay the scatter points and desnity grid to see that the density is working as expected
			#mesh1 = m.pcolormesh(xs_o,ys_o, density_dp,vmin=1,vmax=20,cmap = my_cmap)
			if plot_desert_grid == True:
				lons_dg = [row[0] for row in overlap_desert_grid]
				lats_dg = [row[1] for row in overlap_desert_grid]
				londg,latdg = m(lons_dg, lats_dg)
				oog = m.scatter(londg,latdg, color = 'orange')

				for row in desert_overlap_pts:
					lons_d    = row[0]
					lats_d    = row[1]
					fraction  = row[2]
					lond,latd = m(lons_d, lats_d)
					fraction  = plt.text(lond,latd, str(round(fraction,2)), color='m', fontsize=12)
					#bt = m.scatter(lond,latd)
			

			desert_parameter = np.sum(desert_fraction_list)/total_endpoints
			print 'desert_parameter ', desert_parameter




		#### add land
		if include_land == True:
			overlap_land_grid = []
			#### calc overlap for ocean and enpoints
			#plot a density map of ocean points that is on the same grid as the endpoints
			land_pts = pickle.load(open(land_grid_file, 'rb' ))
			lons_l = [land_pt[0] for land_pt in land_pts]
			lats_l = [land_pt[1] for land_pt in land_pts]
			xs_l,ys_l,density_lp,max_density_lp,lon_bins,lat_bins = INPmod.getGriddedData(nx,ny,lats_l,lons_l,m)
			
			#zip together the density maps for the land and endpoints
			land_fraction_list = []
			land_overlap_pts = []
			i=0
			for row in np.dstack([density_trajs,density_lp]):
				j=0
				for endp_number,land_number in row:
					if endp_number > 0:
						ll_lon = lon_bins[0][j]
						ll_lat = lat_bins[i][0]
						land_fraction = land_number/((2./land_grid_spacing))**2
						land_endpoint_factor = land_fraction*endp_number
						land_fraction_list.append(land_endpoint_factor)

						#for plotting
						if plot_land_grid == True:
							if land_number >0:
								land_overlap_pts.append([ll_lon+grid_size[0]/2,ll_lat+grid_size[1]/2,land_fraction])  #centered
								overlap_land_grid = INPmod.getAreaGridForOverlap(land_pts,ll_lon,ll_lat,grid_size,overlap_land_grid)
					j+=1
				i+=1
			
			#####overlay the scatter points and desnity grid to see that the density is working as expected
			#mesh1 = m.pcolormesh(xs_o,ys_o, density_dp,vmin=1,vmax=20,cmap = my_cmap)
			if plot_land_grid == True:
				lons_lg = [row[0] for row in overlap_land_grid]
				lats_lg = [row[1] for row in overlap_land_grid]
				lonlg,latlg = m(lons_lg, lats_lg)
				oog = m.scatter(lonlg,latlg, color = 'orange')

				for row in land_overlap_pts:
					lons_l    = row[0]
					lats_l    = row[1]
					fraction  = row[2]
					lonl,latl = m(lons_l, lats_l)
					fraction  = plt.text(lonl,latl, str(round(fraction,2)), color='m', fontsize=12)
					#bt = m.scatter(lond,latd)
			

			land_parameter = np.sum(land_fraction_list)/total_endpoints
			print 'land_parameter ', land_parameter



		#### add sea ice and snow
		sea_ice_parameter = 0
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
						sea_ice_fractions.append(sea_ice_area*endp_number/grid_cell_area)
						sea_ice_overlap_pts.append([ll_lon+grid_size[0]/2,ll_lat+grid_size[1]/2,(sea_ice_area/grid_cell_area)])  #centered
					j+=1
				i+=1
			
			sea_ice_parameter = np.sum(sea_ice_fractions)/total_endpoints
			print 'sea_ice_parameter ',sea_ice_parameter
			#patches for plotting
			si_patch_coll = PatchCollection(sea_ice,facecolor='#ffcc00',edgecolor='#ffcc00', alpha = 0.01)
			
			sea_ice_patches = axes.add_collection(si_patch_coll)
			#plt_x,plt_y = m(lons_si,lats_si)
			#si = m.scatter(plt_x,plt_y)
			#sn_patch_coll = PatchCollection(snow,facecolor='white',edgecolor='white', alpha = 0.3)
			#snow_patches = axes.add_collection(sn_patch_coll)
			
			##for plotting si fraction numerical value
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
								overlap_ocean_grid = INPmod.getAreaGridForOverlap(ocean_pts,ll_lon,ll_lat,grid_size,overlap_ocean_grid)
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
					bt = m.scatter(lono,lato)
			

			ocean_overall_parameter = np.sum(ocean_fraction_list)/total_endpoints
			open_water_parameter = ocean_overall_parameter - sea_ice_parameter
			print 'ocean_overall_parameter ', ocean_overall_parameter
			print 'open_water_parameter ', open_water_parameter



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
			np_x,np_y = m(0,90)
			np_marker = m.plot(np_x,np_y, color='k', marker='+')

		##save parameters
		if save_fig == True:
			p_line = [start_time, end_time,round(fire_parameter,3), round(desert_parameter,3), round(open_water_parameter,3), round(sea_ice_parameter,3), round(land_parameter,3)]
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
		

		if save_fig == True:
			os.chdir('/Users/mcallister/projects/INP/MOSSI/footprint analysis '+ str(start_time.year)+ '/')
			plt.savefig('sample' + sample_no + '_' + str(start_time.year)+'-'+str(start_time.month).zfill(2)+'-'+str(start_time.day).zfill(2) + '-' + str(start_time.hour).zfill(2) + str(start_time.minute).zfill(2)  + '_' + str(bt_length) +'day_back-trajectories'+ bl+ '_footprint_v2.pdf',format = 'pdf', bbox_inches='tight') 
		else:
			plt.show()
	
		plt.close()
		i+=1
