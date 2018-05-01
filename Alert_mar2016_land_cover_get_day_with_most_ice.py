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

path = '/Users/mcallister/projects/Alert_INP2016/bin/IMS-24km'
os.chdir(path)

ice_areas = {}
for day in range(11,29):
	date = datetime(2016,3,day)
	day_of_year = date.timetuple().tm_yday
	print date,day_of_year

	ice = 0
	#NSIDC ascii data
	file = 'ims2016'+str(day_of_year).zfill(3)+'_24km_v1.3.asc'
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
					
	print ice
	ice_areas[date] = ice

print max(ice_areas, key=ice_areas.get)
		
