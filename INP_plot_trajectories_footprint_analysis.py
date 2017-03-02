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


location	 			= 'Eureka'
day_to_plot 			= 13				#Alert 	7,8,9  Eureka 11,13  Inuvik 20, 21
sample_no 				= 4					#Alert 7-5, 8-4, 9-3  Eureka 11-4, 13-4  Inuvik 20-45, 21-4
bt_length 				= 20

include_trajectories	= True

include_arctic_circle 	= True

include_oceans			= True

include_fires			= True
fire_threshold			= 80.

include_sea_ice			= True
max_ice_day				= 91 				#Inuvik 103 (april 13)  Eureka 91 (April 1)  Alert 91 (April 1)

include_deserts 		= True

boundary_layer			= True

save_fig				= True

traj_type 				= 'met_ensemble'		#'posn_matrix' 'met_ensemble'
nx, ny 					= 180,90. 				#grid



#### set up the basemap instance  	
sample_date = datetime(2015,4,day_to_plot)
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


#### get trajectories
if traj_type == 'posn_matrix':
	file_location = '/Users/mcallister/projects/INP_Meng/trajectories/'+ location +'-'+ str(bt_length) +'d/sample'+ str(day_to_plot) +'_'+ str(sample_no) + 'w_PBL'
	file_position = 17

if traj_type == 'met_ensemble':
	file_location = '/Users/mcallister/projects/INP_Meng/trajectories/'+ location +'-'+ str(bt_length) +'d/sample'+ str(day_to_plot) +'_'+ str(sample_no) + 'w_ens'
	file_position = 14

endpoints = INPmod.parseTrajectories(location,day_to_plot,sample_no,boundary_layer,file_location, file_position)


#### trajectory heatmap
#get gridded data
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
	MODIS_fires = INPmod.getMODISFires(sample_date,fire_threshold,bt_length)

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
	print 'hours*fires ',np.sum(fire_overlap)/total_endpoints
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
	print 'desert hours ', np.sum(endpoint_counts),np.sum(endpoint_counts)/total_endpoints



#### add sea ice and snow
if include_sea_ice == True:
	sea_ice_hours = 0
	#count all enpoints north of 86deg. This is always frozen, but sea ice point density is low due to converging longitude lines
	for endpoint_lat in lats:
		if endpoint_lat > 86:
			sea_ice_hours += 1

	#calc overlap for sea ice and enpoints
	#plot a density map of sea ice points that is on the same grid as the endpoints
	sea_ice, snow, sea_ice_pts = INPmod.getSeaIceAndSnow(m, max_ice_day)
	lats_si = [row[1] for row in sea_ice_pts]  
	lons_si = [row[0] for row in sea_ice_pts]
	xs_si,ys_si,density_si,max_density_si = INPmod.getGriddedData(nx,ny,lats_si,lons_si,m)
	#mesh1 = m.pcolormesh(xs, ys, density_si,vmin=6,cmap = my_cmap, alpha=1)

	#combine sea ice and trajectory density arrrays and check seaice value.  If seaice value >6 record the number of endpoints (#use 6 b/c of high resolution comapred to ocean data and issues with land overlap).
	for row in np.dstack((density_trajs,density_si)):
		for traj_hours,si_pts in row:
			if si_pts > 6 and traj_hours >0 :    
				sea_ice_hours += traj_hours
	print 'sea ice hours ',sea_ice_hours,sea_ice_hours/total_endpoints
	
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

	print 'ocean hours ',ocean_hours, ocean_hours/total_endpoints
	try:
		print 'open water hours ',ocean_hours-sea_ice_hours, (ocean_hours-sea_ice_hours)/total_endpoints
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
	




#### add text
bl = ''
if boundary_layer == True:
		bl = '_inPBL'
plt.text(0.0, 1.025,'April '+ str(day_to_plot) + ', sample ' + str(sample_no) + bl + ' -' +str(bt_length) + 'days', fontsize = 14,transform=axes.transAxes)

#### save
os.chdir('/Users/mcallister/projects/INP_Meng/')

if save_fig == True:
	plt.savefig(location + '_' + str(day_to_plot) +'-'+ str(sample_no)  + '_' +traj_type + bl + '-' +str(bt_length) + 'day_footprint.pdf',format = 'pdf', bbox_inches='tight') 
plt.show()