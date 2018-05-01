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
from matplotlib import colors
from vincenty import vincenty


include_arctic_circle 	= True
save_fig				= False
plot_distances 			= True
colormapping 			= 'threshold'  #HR, LR, threshold
threshold 				= 0.55


samples = {
#datetime(2014,7,23):[-94.43 ,74.37,0,0],	
#datetime(2014,7,30):[-71.15 ,76.04,0,1],	
#datetime(2014,7,31):[-74.36 ,76.16,0,1],	
#datetime(2014,8,3): [-64.11 ,81.22,1,0],	
#datetime(2014,8,4): [-69.56 ,79.59,0,0],	
#datetime(2014,8,5): [-71.39 ,79.05,1,1],	
#datetime(2014,8,11):[-100.44,69.10,1,1],	
#datetime(2014,8,12):[-105.2 ,68.56,0,1],	
}

samples = {
#datetime(2016,7,20):[-62.1792,60.2987,0,1],	
#datetime(2016,7,28):[-63.3678,67.3911,1,0],	
datetime(2016,8,1): [-70.5039,71.2867,1,1],	
#datetime(2016,8,6): [-71.1903,76.339 ,1,0],	
#datetime(2016,8,8): [-71.7878,76.7296,1,1],	
#datetime(2016,8,9): [-75.716 ,76.3131,1,0],	
#datetime(2016,8,11):[-76.4973,77.7869,0,0],	
#datetime(2016,8,13):[-62.6796,81.334 ,1,1],	
#datetime(2016,8,15):[-74.5626,78.311 ,1,0],	
#datetime(2016,8,21):[-100.817,68.32  ,0,0],	
#datetime(2016,8,23):[-105.5  ,68.9783,1,0],	
}


os.chdir('/Users/mcallister/projects/INP/microlayer/2016/')
for sample in samples:
	print sample
	sample_date = sample
	sample_xoffset = samples[sample][2] #gets correct sample grid cell
	sample_yoffset = samples[sample][3]
	
	sample_lon,sample_lat = samples[sample_date][0],samples[sample_date][1]
	if sample_date.year == 2014:
		conc_file = '/Users/mcallister/projects/INP/NOAA_seaice_concentration/nt_2014' + str(sample_date.month).zfill(2) + str(sample_date.day).zfill(2) + '_f17_v1.1_n.bin'
	if sample_date.year == 2016:
		conc_file = '/Users/mcallister/projects/INP/NOAA_seaice_concentration/nt_2016' + str(sample_date.month).zfill(2) + str(sample_date.day).zfill(2) + '_f18_nrt_n.bin'

	#set up map
	m=Basemap(width=7700000., height=7700000., projection='stere',ellps='WGS84', lon_0=270., lat_0=90, lat_ts=70.,resolution='l')
	fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
	m.drawmapboundary(fill_color='#084B8A')
	m.fillcontinents(color='#D4BD8B',lake_color='#084B8A')
	m.drawcoastlines()
	parallels = np.arange(0.,90,10.)
	m.drawparallels(parallels,labels=[False,True,False,False])
	meridians = np.arange(10.,351.,20.)
	m.drawmeridians(meridians,labels=[False,False,False,True])

	#get sea ice concs
	sea_ice_concs, header_info = INPmod.readConcentrationBinaries(conc_file)

	#define the sea ice grid from known grid specs
	cell_width  = 25000 #meters
	cell_height = 25000 #meters

	ulcnr = [168.35,30.98]
	urcnr = [102.34,31.37]
	lrcnr = [350.03,34.35]
	llcnr = [279.26,33.92]

	grid_coords, grid_xs,grid_ys,grid_center_xys = INPmod.makeConcGrid(m,header_info,cell_width,cell_height,ulcnr,urcnr,lrcnr,llcnr)

	if plot_distances == True:
		center_xs = []
		center_ys = []
		i=0
		for row in grid_center_xys:
			row_center_xs  = [coord[0] for coord in row]
			row_center_ys  = [coord[1] for coord in row]
			center_xs = center_xs + row_center_xs
			center_ys = center_ys + row_center_ys
		
			if (290 <= i < 340 ):
				for coord in row:
					center_x = coord[0]
					center_y = coord[1]
					grid_center_lon, grid_center_lat = m(center_x, center_y, inverse = True)
					grid_center_coords 		= (grid_center_lat,grid_center_lon)
					sample_locn 			= (sample_lat, sample_lon)
					distance_to_sample_locn = vincenty(sample_locn,grid_center_coords)
					m.scatter(center_x,center_y, color = 'g', marker = '.',zorder=300)
					distance  = axes.text(center_x,center_y, str(round(distance_to_sample_locn,1)), color='k')
			i+=1
		

	#draw the arctic circle
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

	#choose appropriate color map
	add_colorbar = False
	if colormapping == 'LR':
		my_cmap = colors.ListedColormap(['#084B8A', '#0174DF','#2E9AFE','#81BEF7','#CEE3F6'])
		add_colorbar = True

	
	if colormapping == 'HR':
		my_cmap = LinearSegmentedColormap.from_list('my_cmap', ['#084B8A', '#2E9AFE','#CEE3F6'], N=250)
		add_colorbar = True

	if colormapping == 'threshold':
		my_cmap = LinearSegmentedColormap.from_list('my_cmap', ['#CEE3F6', '#CEE3F6','#CEE3F6'], N=250)
	
	my_cmap.set_over(color='grey', alpha=1.0)
	my_cmap.set_under(color='grey', alpha=0.0)

	mesh1 = m.pcolormesh(grid_xs,grid_ys,sea_ice_concs,vmin=threshold*250,vmax=250,cmap =my_cmap,edgecolor = 'grey')
	tick_pts = range(0,250,25)
	
	if add_colorbar == True:
		cb1 = plt.colorbar(mesh1,ticks=tick_pts,orientation='horizontal')
		cb1.set_label('percentage sea ice')
		tick_labels = []
		for pt in tick_pts:
			label = round(pt/2.5,0)
			tick_labels.append(label)
		cb1.ax.set_xticklabels(tick_labels)  # horizontal colorbar
		
	sample_x,sample_y = m(sample_lon,sample_lat)
	m.scatter(sample_x,sample_y, color = 'r', marker = '*',s=80,zorder=301)

	#get sea ice conc at sample location
	sample_grid_y,sample_grid_x =  INPmod.find_index_of_nearest_xy(np.array(grid_ys), np.array(grid_xs), sample_y,sample_x)
	print sample_grid_x,sample_grid_y
	print sea_ice_concs[sample_grid_y-sample_yoffset][sample_grid_x-sample_xoffset]/250.0, '***'
	map_coords_y, map_coords_x = grid_coords[sample_grid_y-sample_yoffset][sample_grid_x-sample_xoffset]
	map_lon, map_lat =  m(map_coords_y, map_coords_x, inverse=True)
	#m.scatter(map_coords_y, map_coords_x, color = 'b', marker = '*',s=80,zorder=200)


	plt.xlim(sample_x-7e5, sample_x+7e5)
	plt.ylim(sample_y-7e5, sample_y+7e5)
	
	if save_fig == True:
		plt.savefig('sea_ice_conc_location_plot_'+str(sample_date.date())+ '-55pct_threshold.png', bbox_inches='tight') 

	else:
		plt.show()

