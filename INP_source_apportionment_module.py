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

def getCoordFromDB(origin_lon,origin_lat,radius_earth,bearing, distance):
	lat1 = math.radians(origin_lat) #Current lat point converted to radians
	lon1 = math.radians(origin_lon) #Current long point converted to radians

	lat2 = math.asin( math.sin(lat1)*math.cos(distance/radius_earth) +
	     math.cos(lat1)*math.sin(distance/radius_earth)*math.cos(bearing))

	lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(distance/radius_earth)*math.cos(lat1),
	             math.cos(distance/radius_earth)-math.sin(lat1)*math.sin(lat2))

	lat2 = math.degrees(lat2)
	lon2 = math.degrees(lon2)

	return lon2, lat2


def getSeaIceAndSnow(bmap,year,day_of_year):
	si_patches = []
	sn_patches = []
	#binary arrays
	path = '/Users/mcallister/projects/INP/NOAA snow and ice 4km/'
	os.chdir(path)

	file_lon = 'imslon_4km.bin'
	file_lat = 'imslat_4km.bin'

	f_lon = open(file_lon, 'rb')
	f_lat = open(file_lat, 'rb')

	lons_s = np.fromfile(f_lon, dtype='<f4')
	lats_s = np.fromfile(f_lat, dtype='<f4')

	lons = np.reshape(lons_s, [6144,6144], order='C')
	lats = np.reshape(lats_s, [6144,6144], order='C')

	f_lon.close()
	f_lat.close()

	#NSIDC ascii data
	file = 'ims'+str(year)+str(175).zfill(3)+'_4km_v1.2.asc'
	print file
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
				lon_o = -(lons[row][col] - 20)
				if lon_o < -180:
					lon_o = 180-(-180-lon_o)

				cell_side_length = 4000#23684.997 #(23,684.997 meters per cell in x and y)
				cell_hypotenuse = math.sqrt((cell_side_length**2)*2)
				radius_of_earth = 6371200.0  #meters 
				#move marker to center of cell 
				if value in [3]:
					lon_center,lat_center = lon_o,lat_o,#getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(45), (cell_hypotenuse/2))

					if lat_center > 40:
						sea_ice_pts.append([lon_center,lat_center])
				
					#now make the patches for display
					if np.isnan(lon_o) == False and np.isnan(lat_o) == False and lat_o >= 0:
						lon_1,lat_1 = getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(315),cell_hypotenuse/2)
						lon_2,lat_2 = getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(45),cell_hypotenuse/2)
						lon_3,lat_3 = getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(135),cell_hypotenuse/2)
						lon_4,lat_4 = getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(225),cell_hypotenuse/2)
						p = Polygon([bmap(lon_1,lat_1),bmap(lon_2,lat_2),bmap(lon_3,lat_3),bmap(lon_4,lat_4)]) 
						if value == 3:
							si_patches.append(p)
						if value == 4:
							sn_patches.append(p)
				col +=1
			row+=1

	#print len(si_patches), ' sea ice pixels'
	#print len(sn_patches), ' snow pixels'
	return si_patches,sn_patches, sea_ice_pts



def getMODISFires(sample_date,fire_threshold,bt_length,MODIS_file):
	fire_list = []
	file = '/Users/mcallister/projects/INP/MODIS fire data/'+ MODIS_file
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

def getDesertShapes(bmap):
	patches = []
	names 	= []
	#shapefile citation 'Made with Natural Earth. Free vector and raster bmap data @ naturalearthdata.com.''
	bmap.readshapefile('/Users/mcallister/projects/INP/ne_50m_geography_regions_polys/ne_50m_geography_regions_polys', 'regions', drawbounds = False)
	for info, shape in zip(bmap.regions_info, bmap.regions):
		if info['featurecla'] == 'Desert' and (info['region'] in['Asia' ,'North America' , 'Europe','Oceania']):
			name = info['name']
			names.append(name)
			patches.append(Polygon(np.array(shape), True))

 	return names,patches


def parseTrajectories(location,day_to_plot,sample_no,boundary_layer,bt_length,file_location,file_position):
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
				#print file
				tdump_file = open(file, 'r')
				data_start = False
				file_trajectories = {}
				for line in tdump_file:
					newline = line.split()
					if data_start == True:
						hours_along = float(newline[8])
						lat 		= float(newline[9])
						lon 		= float(newline[10])
						height 		= float(newline[11]) # in m AMSL
						rain 		= float(newline[13])
						mixed_depth = float(newline[14]) # in m AGL
						terrain_ht	= float(newline[15]) # in m
						endpoint 	= [lat, lon, height]
						
						#allow 20d bts to be used for shorter times
						if abs(hours_along) > bt_length*24: 
							break
						if boundary_layer == True: 
							if height < (terrain_ht + mixed_depth):
								endpoints.append(endpoint)
						else:
							endpoints.append(endpoint)
					
					if newline[1] == 'PRESSURE':
						data_start = True
					
				tdump_file.close() 

	return endpoints


def parseMOSSITrajectories(file_location,start_time,end_time,boundary_layer,bt_length):
	os.chdir(file_location)
	endpoints = []
	for file in os.listdir('.'):
		if file.startswith('INP_MOSSI'):  
			file_date_time = parser.parse(file[10:-6])
			if start_time <= file_date_time <= end_time:			
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
						height 		= float(newline[11]) # in m AMSL
						rain 		= float(newline[13])
						mixed_depth = float(newline[14]) # in m AGL
						terrain_ht	= float(newline[15]) # in m
						endpoint 	= [lat, lon, height]
						
						#allow 20d bts to be used for shorter times
						if abs(hours_along) > bt_length*24: 
							break
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


def getGriddedData(nx,ny,lats,lons,bmap):
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
	xs, ys = bmap(lon_bins_2d, lat_bins_2d)

	return xs,ys,density,density.max(),lon_bins_2d, lat_bins_2d





def find_index_of_nearest_xy(y_array, x_array, y_point, x_point):
    distance = (y_array-y_point)**2 + (x_array-x_point)**2
    idy,idx = np.where(distance==distance.min())
   
    return idy[0],idx[0]



def haversine(lon1, lat1, lon2, lat2,radius_earth):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    m = radius_earth * c
    
    return m

def getOceanGridForOverlap(ocean_pts,ll_lon,ll_lat,grid_size,overlap_grid_pts_list):
		for row in ocean_pts:
			opglon = row[0]
			opglat = row[1]
			if (ll_lon <= opglon < (ll_lon+grid_size[0])) and (ll_lat <= opglat < (ll_lat+grid_size[1])):
				overlap_grid_pts_list.append([opglon,opglat])

		return overlap_grid_pts_list

