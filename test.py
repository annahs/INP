import os
import sys
from pprint import pprint
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.path import Path
import pickle
import INP_source_apportionment_module as INPmod

lons = [4.2,5.5,6.5]
lats = [1.5,2.5,3.5]

lon_bins = np.linspace(0, 10, 5+1)
lat_bins = np.linspace(0, 5,  5+1)

# Histogram the lats and lons to produce an array of frequencies in each box.
# Because histogram2d does not follow the cartesian convention 
# (as documented in the np.histogram2d docs)
# we need to provide lats and lons rather than lons and lats
density, _, _ = np.histogram2d(lats, lons, [lat_bins, lon_bins])
density2, _, _ = np.histogram2d(lats, lons, [lat_bins, lon_bins])

# Turn the lon/lat bins into 2 dimensional arrays ready 
# for conversion into projected coordinates
lon_bins_2d, lat_bins_2d = np.meshgrid(lon_bins, lat_bins)


print lon_bins_2d
print lat_bins_2d
print density

pprint(np.dstack((density,density2)))

i=0
for row in np.dstack((density,density2)):
	j=0
	for d1,d2 in row:
		if d1 >0:
			print i,j,'**'
			print lon_bins_2d[0][j]
			print lat_bins_2d[i][0]
		j+=1	
	i+=1
