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

def getSeaIceAndSnow(map,day_of_year):
	si_patches = []
	sn_patches = []
	#binary arrays
	path = '/Users/mcallister/projects/INP_Meng/NOAA snow and ice/'
	os.chdir(path)

	file_lon = 'imslon_24km.bin'
	file_lat = 'imslat_24km.bin'

	f_lon = open(file_lon, 'rb')
	f_lat = open(file_lat, 'rb')

	lons_s = np.fromfile(f_lon, dtype='<f4')
	lats_s = np.fromfile(f_lat, dtype='<f4')

	lons = np.reshape(lons_s, [1024,1024], order='C')
	lats = np.reshape(lats_s, [1024,1024], order='C')

	f_lon.close()
	f_lat.close()

	#NSIDC ascii data
	file = 'ims2015'+str(day_of_year).zfill(3)+'_24km_v1.3.asc'
	sea_ice_pts = []
	with open(file, 'r') as f:
		for line in range(0,30):
			f.readline()
		row=0
		for line in f:
			newline = list(line)[:-1]
			col = 0
			for item in newline:
				value = int(item)
				lat_o = lats[row][col]
				lon_o = lons[row][col] - 20
				if lon_o < -180:
					lon_o = 180-(-180-lon_o)

				#move marker to center of 24x24 cell (11842.495 is half width of cell(23,684.997 meters per cell in x and y))
				if value == 3:
					lat_center = lat_o  + (11842.495/6371200.0) * (180 / math.pi);
					lon_center = lon_o  + (11842.495/6371200.0) * (180 / math.pi) / math.cos(math.radians(lat_o * math.pi/180));
					sea_ice_pts.append([-lon_center,lat_center])
				
				#now make the patches for display
				if np.isnan(lon_o) == False and np.isnan(lat_o) == False and lat_o >= 0:
					if value == 3:
						x1,y1 = map(-lon_o,lat_o)
						x2,y2 = map(-(lon_o+(23684.997/6371200.0)*(180/math.pi)/math.cos(math.radians(lat_o*math.pi/180))),lat_o)
						x3,y3 = map(-lon_o,lat_o-(23684.997/6371200.0)*(180 / math.pi))
						x4,y4 = map(-(lon_o+(23684.997/6371200.0)*(180/math.pi)/math.cos(math.radians(lat_o*math.pi/180))),(lat_o-(23684.997/6371200.0)*(180 / math.pi)))
						p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)]) 
						si_patches.append(p)
					if value == 4:
						x1,y1 = map(-lon_o,lat_o)
						x2,y2 = map(-(lon_o+(23684.997/6371200.0)*(180/math.pi)/math.cos(math.radians(lat_o*math.pi/180))),lat_o)
						x3,y3 = map(-lon_o,lat_o-(23684.997/6371200.0)*(180 / math.pi))
						x4,y4 = map(-(lon_o+(23684.997/6371200.0)*(180/math.pi)/math.cos(math.radians(lat_o*math.pi/180))),(lat_o-(23684.997/6371200.0)*(180 / math.pi)))
						p = Polygon([(x1,y1),(x2,y2),(x4,y4),(x3,y3)]) 
						sn_patches.append(p)
				col +=1
			row+=1

	#print len(si_patches), ' sea ice pixels'
	#print len(sn_patches), ' snow pixels'
	return si_patches,sn_patches, sea_ice_pts


def getMODISFires(sample_date,fire_threshold,bt_length):
	fire_list = []
	file = '/Users/mcallister/projects/INP_Meng/MODIS fire data/fire_archive_M6_6849.txt'
	with open(file, 'r') as f:
		f.readline()
		for line in f:
			newline = line.split()
			lat 			= float(newline[0])
			lon 			= float(newline[1])
			scan			= float(newline[3]) # scan is roughly east-west
			track 			= float(newline[4])	# track is roughly north-south
			acq_date_time	= parser.parse(newline[5] + ' ' + newline[6].zfill(4))
			confidence		= float(newline[9]) #0-30=low confidence 30-80 =nominal 80-100=high -  http://www.fao.org/fileadmin/templates/gfims/docs/MODIS_Fire_Users_Guide_2.4.pdf section 7.4.3
			
			#get all fires within the window if interest
			if confidence >= fire_threshold:
				if (sample_date - timedelta(days = bt_length)) <= acq_date_time <= sample_date:
					fire_list.append([acq_date_time,lat,lon,scan,track])

	print len(fire_list), ' fires'
	return fire_list

def getDesertShapes(map):
	patches = []
	names 	= []
	#shapefile citation 'Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.''
	map.readshapefile('/Users/mcallister/projects/INP_Meng/ne_50m_geography_regions_polys/ne_50m_geography_regions_polys', 'regions', drawbounds = False)
	for info, shape in zip(map.regions_info, map.regions):
		if info['featurecla'] == 'Desert' and (info['region'] in['Asia' ,'North America' , 'Europe','Oceania']):
			name = info['name']
			names.append(name)
			patches.append(Polygon(np.array(shape), True))

 	return names,patches


def parseTrajectories(location,day_to_plot,sample_no,boundary_layer,file_location,file_position):
	os.chdir(file_location)
	file_posn = file_position
	endpoints = []
	for file in os.listdir('.'):
		if file.startswith('INP_' + location):  
			sample_posn_start = file_posn + len(location)
			sample_number = int(file[sample_posn_start:(sample_posn_start+1)])
			day 	= int(file[(sample_posn_start+6):(sample_posn_start+8)])
			hour 	= int(file[(sample_posn_start+8):(sample_posn_start+10)])
			minute 	= int(file[(sample_posn_start+10):(sample_posn_start+12)])
			traj_time = datetime(2015,4,day,hour,minute)
			
			if day == day_to_plot and sample_number == sample_no:
				print file
				tdump_file = open(file, 'r')
				data_start = False
				file_trajectories = {}
				for line in tdump_file:
					newline = line.split()
					if data_start == True:
						lat 		= float(newline[9])
						lon 		= float(newline[10])
						height 		= float(newline[11]) # in m AMSL
						rain 		= float(newline[13])
						mixed_depth = float(newline[14]) # in m AGL
						terrain_ht	= float(newline[15]) # in m
						endpoint 	= [lat, lon, height]
						if boundary_layer == True: 
							if height < (terrain_ht + mixed_depth):
								endpoints.append(endpoint)
						else:
							endpoints.append(endpoint)
					
					if newline[1] == 'PRESSURE':
						data_start = True
					
				tdump_file.close() 

	return endpoints

def makeColormap(c1,c2,c3,max_density):
	colors = [c1,c2,c3]  
	n_bins = max_density
	my_cmap = LinearSegmentedColormap.from_list('my_cmap', colors, N=n_bins)
	my_cmap.set_under('w',alpha=0.0)
	my_cmap.set_bad('w',alpha=0.0)

	return my_cmap


def getGriddedData(nx,ny,lats,lons,map):
	# compute appropriate bins to histogram the data into
	lon_bins = np.linspace(-180, 180, nx+1)
	lat_bins = np.linspace(-90, 90, ny+1)
	# Histogram the lats and lons to produce an array of frequencies in each box.
	# Because histogram2d does not follow the cartesian convention 
	# (as documented in the np.histogram2d docs)
	# we need to provide lats and lons rather than lons and lats
	density, _, _ = np.histogram2d(lats, lons, [lat_bins, lon_bins])

	# Turn the lon/lat bins into 2 dimensional arrays ready 
	# for conversion into projected coordinates
	lon_bins_2d, lat_bins_2d = np.meshgrid(lon_bins, lat_bins)

	# convert the xs and ys to map coordinates
	xs, ys = map(lon_bins_2d, lat_bins_2d)

	return xs,ys,density,density.max()


def find_index_of_nearest_xy(y_array, x_array, y_point, x_point):
    distance = (y_array-y_point)**2 + (x_array-x_point)**2
    idy,idx = np.where(distance==distance.min())
   
    return idy[0],idx[0]
