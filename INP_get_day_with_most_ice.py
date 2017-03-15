import numpy as np
from struct import *
import sys
import os
import math
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import matplotlib.colors

#Note: With respect to the ASCII text data files, the lat/lon grids are flipped in orientation. 
#Specifically, the binary arrays are stored beginning with the upper left corner, whereas the ASCII text data are stored beginning with the lower left corner. 
#Please be aware of this when working with these files.


dates = []
for julian_day in range(175,224):
	dates.append(datetime(2014,1,1) + timedelta(days=julian_day-1))


path = '/Users/mcallister/projects/INP/NOAA snow and ice/'
os.chdir(path)

ice_extents = {}
for date in dates:
	ice = 0
	day_of_year = date.timetuple().tm_yday

	#NSIDC ascii data
	file = 'ims2014'+str(day_of_year).zfill(2)+'_24km_v1.2.asc'
	plot_data = []
	with open(file, 'r') as f:
		for line in range(0,30):
			f.readline()
		for line in f:
			newline = list(line)[:-1]
			for item in newline:
				value = int(item)
				if value == 3:
					ice +=1

	print date,day_of_year, ice
	ice_extents[date] = ice

max_day = max(ice_extents, key=ice_extents.get)
print '***',max_day, ice_extents[max_day]
		
