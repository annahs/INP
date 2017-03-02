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
dates = [

datetime(2015,3,31),
datetime(2015,4,1),
datetime(2015,4,2),
datetime(2015,4,3),
datetime(2015,4,4),
datetime(2015,4,5),
datetime(2015,4,5),
datetime(2015,4,6),
datetime(2015,4,8),
datetime(2015,4,7),
datetime(2015,4,9),

]

path = '/Users/mcallister/projects/INP_Meng/NOAA snow and ice/'
os.chdir(path)

for date in dates:
	ice = 0
	day_of_year = date.timetuple().tm_yday
	print date,day_of_year

	#NSIDC ascii data
	file = 'ims20150'+str(day_of_year)+'_24km_v1.3.asc'
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
		