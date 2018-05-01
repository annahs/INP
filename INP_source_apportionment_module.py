import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import os
import sys
import glob
from struct import *
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
from dateutil import parser
import math
from matplotlib.colors import LinearSegmentedColormap
import FLEXPART_PES_NETCARE_module as PES


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


def getSeaIceAndSnow(bmap,year,day_of_year, resolution = 4):
	si_patches = []
	sn_patches = []
	#binary arrays
	path = '/Users/mcallister/projects/INP/NOAA snow and ice '+str(resolution)+'km/'
	os.chdir(path)

	file_lon = 'imslon_'+str(resolution)+'km.bin'
	file_lat = 'imslat_'+str(resolution)+'km.bin'

	f_lon = open(file_lon, 'rb')
	f_lat = open(file_lat, 'rb')

	lons_s = np.fromfile(f_lon, dtype='<f4')
	lats_s = np.fromfile(f_lat, dtype='<f4')

	if resolution == 4:
		grid_res = 6144
		cell_side_length = 4000
	if resolution == 24:
		grid_res = 1024
		cell_side_length = 23684.997

	cell_hypotenuse = math.sqrt((cell_side_length**2)*2)
	radius_of_earth = 6371200.0  #meters 

	lons = np.reshape(lons_s, [grid_res,grid_res], order='C')
	lats = np.reshape(lats_s, [grid_res,grid_res], order='C')

	f_lon.close()
	f_lat.close()

	#NSIDC ascii data
	if year == 2014:
		version = '1.2'
	if year == 2016:
		version = '1.3'

	file = 'ims'+str(year)+str(day_of_year).zfill(3)+'_'+str(resolution)+'km_v'+version+'.asc'
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

				#move marker to center of cell 
				if value in [3,4]:
					lon_center,lat_center = lon_o,lat_o#getCoordFromDB(lon_o,lat_o,radius_of_earth,math.radians(45), (cell_hypotenuse/2))
				
					#now make the patches for display
					if np.isnan(lon_o) == False and np.isnan(lat_o) == False and lat_o >= 0:
						lon_1,lat_1 = getCoordFromDB(lon_center,lat_center,radius_of_earth,math.radians(315),cell_hypotenuse/2)
						lon_2,lat_2 = getCoordFromDB(lon_center,lat_center,radius_of_earth,math.radians(45),cell_hypotenuse/2)
						lon_3,lat_3 = getCoordFromDB(lon_center,lat_center,radius_of_earth,math.radians(135),cell_hypotenuse/2)
						lon_4,lat_4 = getCoordFromDB(lon_center,lat_center,radius_of_earth,math.radians(225),cell_hypotenuse/2)
						p = Polygon([bmap(lon_1,lat_1),bmap(lon_2,lat_2),bmap(lon_3,lat_3),bmap(lon_4,lat_4)]) 
						if value == 3:
							si_patches.append(p)
							sea_ice_pts.append([lon_center,lat_center])
						if value == 4:
							sn_patches.append(p)
				col +=1
			row+=1

	print len(si_patches), ' sea ice pixels'
	print len(sn_patches), ' snow pixels'
	return si_patches,sn_patches, sea_ice_pts



def getMODISFires(sample_date,fire_threshold,bt_length,MODIS_file, min_lat = -91, max_lat = 91, min_lon = -181, max_lon = 181):
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
			frp				= float(newline[12])

			#get all fires within the window if interest
			if confidence >= fire_threshold and frp >0 and (min_lat <= lat < max_lat) and (min_lon <= lon < max_lon):
				if (sample_date - timedelta(days = bt_length)) <= acq_date_time <= sample_date:
					fire_list.append([acq_date_time,lat,lon,scan,track,frp])

	print len(fire_list), ' fires'
	return fire_list

def getDesertShapes(bmap):
	patches = []
	names 	= []
	#shapefile citation 'Made with Natural Earth. Free vector and raster bmap data @ naturalearthdata.com.''
	bmap.readshapefile('/Users/mcallister/projects/INP/ne_50m_geography_regions_polys/ne_50m_geography_regions_polys', 'regions', drawbounds = False)
	for info, shape in zip(bmap.regions_info, bmap.regions):
		if info['featurecla'] == 'Desert':# and (info['region'] in['Asia' ,'North America' , 'Europe','Oceania']):
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


def parseMOSSITrajectories(file_location,start_time,end_time,boundary_layer,bt_length,low_alt):
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
						traj_number = float(newline[0])
						
						#if at low altitude do no use downward displacement of meteo grid
						if low_alt == True:
							if 9 < (traj_number) <= 18:
								continue

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
	my_cmap.set_over('w',alpha=0.0)
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
    distance = radius_earth * c
    
    return distance

def getAreaGridForOverlap(area_pts,ll_lon,ll_lat,grid_size,overlap_grid_pts_list):
		for row in area_pts:
			opglon = row[0]
			opglat = row[1]
			if (ll_lon <= opglon < (ll_lon+grid_size[0])) and (ll_lat <= opglat < (ll_lat+grid_size[1])):
				overlap_grid_pts_list.append([opglon,opglat])

		return overlap_grid_pts_list


def readConcentrationBinaries(file):
	with open(file, 'r') as f:
		header = f.read(300)

		header_labels = getSeaIceHeaderLabels()
		header_info_dict = {}
		start_byte = 0
		i = 0
		while i <21:
			val = header[start_byte:start_byte+6]
			start_byte += 6
			header_info_dict[header_labels[i]] = val
			i+=1
		
		header_info_dict['file name'] = header[start_byte:start_byte+24]
		header_info_dict['image title'] = header[start_byte:start_byte+80]
		header_info_dict['data information'] = header[start_byte:start_byte+70]
		
		file_data = f.read(136192)
		start_byte = 0
		data_list = []
		for row in range(0,int(header_info_dict['Number of rows in polar stereographic grid'][0:5])):
			newline = []
			for column in range(0,int(header_info_dict['Number of columns in polar stereographic grid'][0:5])):
				conc_val = unpack('B',file_data[start_byte:start_byte+1])
				newline.append(int(conc_val[0]))
				start_byte +=1

			data_list.append(newline)
		data_array = np.array(data_list)

		return data_array, header_info_dict

def makeConcGrid(bmap,header_info_dict,cell_width,cell_height,ulcnr,urcnr,lrcnr,llcnr):
	ulcnr_x,ulcnr_y = bmap(ulcnr[0], ulcnr[1])
	urcnr_x,urcnr_y = bmap(urcnr[0], urcnr[1])
	lrcnr_x,lrcnr_y = bmap(lrcnr[0], lrcnr[1])
	llcnr_x,llcnr_y = bmap(llcnr[0], llcnr[1])

	rise = urcnr_y-ulcnr_y
	run  = urcnr_x-ulcnr_x

	skew_angle = math.atan(rise/run)
	#print 'angle',  math.degrees(skew_angle)

	y_displ_col = cell_width*math.sin(skew_angle)
	x_displ_col = cell_width*math.cos(skew_angle)
	y_displ_row = x_displ_col
	x_displ_row = y_displ_col

	grid_coords = []
	grid_center_xys = []
	grid_ys = []
	grid_xs = []
	cell_center_x_start = ulcnr_x + (x_displ_row/2) + (x_displ_col/2)  
	cell_center_y_start = ulcnr_y - (y_displ_row/2) + (y_displ_col/2)
	for row in range(0,int(header_info_dict['Number of rows in polar stereographic grid'][0:5])):
		newline = []
		newline_c = []
		lon_line = []
		lat_line = []
		cell_corner_x = ulcnr_x + row*x_displ_row
		cell_corner_y = ulcnr_y - row*y_displ_row
		cell_center_x = cell_center_x_start + row*x_displ_row
		cell_center_y = cell_center_y_start - row*y_displ_row

		for column in range(0,int(header_info_dict['Number of columns in polar stereographic grid'][0:5])):	
			newline.append((cell_corner_x,cell_corner_y))
			newline_c.append((cell_center_x,cell_center_y))
			lon_line.append(cell_corner_x)
			lat_line.append(cell_corner_y)
			
			cell_center_x += x_displ_col
			cell_center_y += y_displ_col

			cell_corner_x += x_displ_col
			cell_corner_y += y_displ_col
				
		grid_coords.append(newline)
		grid_center_xys.append(newline_c)
		grid_xs.append(lon_line)
		grid_ys.append(lat_line)
		
		grid_center_xys

	return grid_coords, grid_xs,grid_ys, grid_center_xys



def getSeaIceHeaderLabels():
	header_labels = [
	'Missing data integer value',
	'Number of columns in polar stereographic grid',
	'Number of rows in polar stereographic grid',
	'Unused/internal',
	'Latitude enclosed by polar stereographic grid',
	'Greenwich orientation of polar stereographic grid',
	'Unused/internal',
	'J-coordinate of the grid intersection at the pole',
	'I-coordinate of the grid intersection at the pole',
	'Five-character instrument descriptor (SMMR, SSM/I, SSMIS)',
	'Two descriptors of two characters each that describe the data; (for example, 07 cn = Nimbus-7 ice concentration)',
	'Starting Julian day of grid data',
	'Starting hour of grid data (if available)',
	'Starting minute of grid data (if available)',
	'Ending Julian day of grid data',
	'Ending hour of grid data (if available)',
	'Ending minute of grid data (if available)',
	'Year of grid data',
	'Julian day of grid data',
	'Three-digit channel descriptor (000 for ice concentrations)',
	'Integer scaling factor',
	]

	return header_labels


def mapValue(value, input_min, input_max, output_min, output_max):
    # Figure out how 'wide' each range is
    leftSpan = input_max - input_min
    rightSpan = output_max - output_min

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - input_min) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return output_min + (valueScaled * rightSpan)


 
def calcPolygonOverlapArea(poly1, poly2, fraction):
	intersection_poly = None
	if poly1.within(poly2):
		fraction = 1.
		return fraction, intersection_poly
	elif poly1.intersects(poly2):
		intersections = poly1.intersection(poly2)
		for intersection in intersections:
			fraction += intersection.area()/poly1.area()	
			intersection_poly = Polygon(intersection.boundary)

	return fraction, intersection_poly



def getAveragedAlert2016PES(sample_times, footprint_layer_height, days_back):
	summed_conc = []
	sim_count = 0
	
	days_back_str = str(days_back)
	if days_back == 20:
		days_back_str = ''


	for sample in sample_times:
		start_time = PES.valid_date(sample[0])
		end_time   = PES.valid_date(sample[1])
		current_time = datetime(start_time.year,start_time.month,start_time.day,start_time.hour + 1)
		while current_time <= end_time:
			base_path 		= '/Volumes/storage/FLEXPART/Alert_2016/FLEXPART_2016_dkunkel/'
			sim_path        = os.path.join(base_path,str(current_time.year) + str(current_time.month).zfill(2)+ str(current_time.day).zfill(2) + str(current_time.hour).zfill(2) + '0000/')
			try:
				p_data          = glob.glob(sim_path+'summedPES_' + days_back_str + '*.h5')[0]
			except:
				print 'no file', current_time
				current_time += timedelta(hours=1)
				continue
			
			p_nc_data       = glob.glob(sim_path+'grid_time_*.nc')[0]
			#getprint p_nc_data

			#get the previously summed PES information
			Conc_var = PES.get_var(p_data, 'Conc_pCol' + str(footprint_layer_height)) #Conc_tCol Conc_pCol300

			xlat_i = PES.get_var(p_nc_data, 'latitude')
			xlon_i = PES.get_var(p_nc_data, 'longitude')

			xlon,xlat = np.meshgrid(xlon_i,xlat_i)

			if xlon.shape != Conc_var.shape or  xlat.shape != Conc_var.shape:
				print "DIFFERENT GRID SHAPES!"
				sys.exit()

			#append to the list of the concentration fields
			summed_conc.append(Conc_var)
			current_time += timedelta(hours=1)
			sim_count +=1

	avgd_PES = np.mean(np.array(summed_conc), axis=0 )
	return avgd_PES, sim_count
