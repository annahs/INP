import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
import math
from datetime import datetime
import calendar
import SP2_utilities
from pysplit import trajectory_generator
from dateutil import parser
import itertools


station = 'Alert'
day = 9
sample_number = 3   #Alert 7-4, 8-4, 9-3  Eureka 11-3, 13-4  Inuvik 20-45, 21-4
duration = -480 #negative for back trajectories
minute_interval = 2
mossi_file = '/Users/mcallister/projects/INP/MOSSI/MOSSI_sampling_2014-v2_b.txt'

def addDistance(lat0,lon0,delta):
	lat = lat0 + (180./math.pi)*(delta/6371000.)
 	lon = lon0 + (180./math.pi)*(delta/6371000.)/math.cos(lat0)

 	return lat, lon


def createCartesianProduct(heights, lats, lons):
	iterables = [heights, lats, lons]
	cp = []
	for t in itertools.product(*iterables):
		cp.append(t)

	return cp


#all samples for a station (start, mid, end)
def allsamples(station):
	file = '/Users/mcallister/projects/INP_Meng/INP_' + station + '.txt'
	with open(file,'r') as f:
		f.readline()	
		for line in f:
			newline = line.split()	
			month 	= newline[0]
			day 	= newline[1]
			sample	= int(newline[2])
			time	= newline[4]
			lat 	= float(newline[5])
			lon 	= float(newline[6])
			alt 	= float(newline[7])
			date_time = month + ' ' + day + ' ' + '2015' + ' ' + time
			sample_time = parser.parse(date_time)

			trajectory_generator.generate_bulktraj(
				'INP_Eureka_', sample, r'/Users/mcallister/Hysplit4/working',
				r'/Users/mcallister/projects/INP/trajectories/' + station + ' '+ str(duration/24) +'d', r'/Users/mcallister/Hysplit4/met_files',
				[sample_time.year], [sample_time.month], [sample_time.hour],[sample_time.minute],
				[alt], (lat, lon), -240, monthslice=slice((sample_time.day-1), sample_time.day, 1),hysplit='/Users/mcallister/Hysplit4/exec/hyts_std')

#a specific sample (minute resolution typically)
def sampleX(station, day, sample_number):
	file = '/Users/mcallister/projects/INP/INP_' + station + '_sample_' + str(day) + '_' + str(sample_number) + '.txt'
	with open(file,'r') as f:
		f.readline()	
		f.readline()	
		for line in f:
			newline = line.split()
			date 	= newline[0]
			time	= newline[1]
			lat 	= float(newline[5])
			lon 	= float(newline[6])
			alt 	= float(newline[7])
			date_time = date + ' ' + time 
			sample_time = parser.parse(date_time,dayfirst=True)

			if sample_time.second == 0 and (sample_time.minute % minute_interval) == 0:
				print sample_time
				trajectory_generator.generate_bulktraj(
					'INP_'+station+'_'+ str(day) + '_', sample_number, r'/Users/mcallister/Hysplit4/working',
					r'/Users/mcallister/projects/INP/trajectories/' + station + str(duration/24) +'d/sample' + str(day) + '_' + str(sample_number) + 'w_ens/', r'/Users/mcallister/Hysplit4/met_files',
					[sample_time.year], [sample_time.month], [sample_time.hour],[sample_time.minute],
					[alt], (lat, lon), duration, monthslice=slice((sample_time.day-1), sample_time.day, 1),hysplit='/Users/mcallister/Hysplit4/exec/hyts_ens')

def MOSSIsamples(file,duration):
	with open(file,'r') as f:
		f.readline()	
		for line in f:
			newline = line.split()
			date 	= newline[0]
			time	= newline[1]
			lat 	= float(newline[2])
			lon 	= float(newline[3])
			alt 	= 15#float(newline[2])
			date_time = date + ' ' + time 
			sample_time = parser.parse(date_time)
			print sample_time
			trajectory_generator.generate_bulktraj(
				'INP_MOSSI_', 0, r'/Users/mcallister/Hysplit4/working',
				r'/Users/mcallister/projects/INP/MOSSI/trajectories/', r'/Users/mcallister/Hysplit4/met_files',
				[sample_time.year], [sample_time.month], [sample_time.hour],[sample_time.minute],
				[alt], (lat, lon), duration, monthslice=slice((sample_time.day-1), sample_time.day, 1),hysplit='/Users/mcallister/Hysplit4/exec/hyts_ens')


#a specific sample with a grid of points at each minute
def sampleXGrid(station, day, sample_number):

	file = '/Users/mcallister/projects/INP/INP_' + station + '_sample_' + str(day) + '_' + str(sample_number) + '.txt'
	with open(file,'r') as f:
		f.readline()	
		f.readline()	
		for line in f:
			newline = line.split()
			date 	= newline[0]
			time	= newline[1]
			lat 	= float(newline[5])
			lon 	= float(newline[6])
			alt 	= float(newline[7])
			date_time = date + ' ' + time 
			sample_time = parser.parse(date_time)
			print lat, lon, alt

			if sample_time.second == 0 and (sample_time.minute % 5) == 0:  # every 5 mins
				print sample_time
				heights = []
				lats = []
				lons = [] 				
				for displacement in [-250,-125,0,125,250]:
					new_lat, new_lon = addDistance(lat,lon,displacement)
					new_height  = alt + displacement
					lats.append(new_lat)
					lons.append(new_lon)
					heights.append(new_height)
					cp = createCartesianProduct(heights, lats, lons)
				pprint(cp)

				i=0
				for row in cp:
					alt_pt = row[0]
					lat_pt = row[1]
					lon_pt = row[2]
					i+=1


					trajectory_generator.generate_bulktraj(
						'INP_Inuvik_20_'+str(i).zfill(3), sample_number, r'/Users/mcallister/Hysplit4/working',
						r'/Users/mcallister/projects/INP/trajectories/' + station + ' 10d/sample' + str(day) + '_' + str(sample_number) + 'w_PBL/', r'/Users/mcallister/Hysplit4/met_files',
						[sample_time.year], [sample_time.month], [sample_time.hour],[sample_time.minute],
						[alt_pt], (lat_pt, lon_pt), -240, monthslice=slice((sample_time.day-1), sample_time.day, 1),hysplit='/Users/mcallister/Hysplit4/exec/hyts_std')

MOSSIsamples(mossi_file,duration)
#sampleX(station, day, sample_number)
