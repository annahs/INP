import os
import sys
from pprint import pprint
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.path import Path
import pickle



radius_earth = 6371200.0


m=Basemap(width=9000000., height=9000000., projection='stere',rsphere=radius_earth, lon_0=270., lat_0=90., lat_ts=60.)
land_polygons = [Path(p.boundary) for p in m.landpolygons]


fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
m.drawcoastlines()
#m.drawcountries()
parallels = np.arange(0.,90,10.)
m.drawparallels(parallels,labels=[False,True,False,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[False,False,False,True])


# compute appropriate bins to histogram the data into
nx = 720
ny = 180
lon_bins = np.linspace(-179.25, 180.75, nx+1)
lat_bins = np.linspace(-0.25, 89.75, ny+1)

# Turn the lon/lat bins into 2 dimensional arrays ready 
# for conversion into projected coordinates
lon_bins_2d, lat_bins_2d = (np.meshgrid(lon_bins, lat_bins))
xs, ys = m(lon_bins_2d, lat_bins_2d)

plot_list = []
land_list 	= []
for row in np.dstack((xs, ys)):
	for xpt,ypt in row:
		for land_polygon in land_polygons:
			if land_polygon.contains_point([xpt,ypt], transform=None, radius=0.0):
				lon,lat = m(xpt,ypt, inverse=True)
				land_list.append([lon,lat])
				plot_list.append([xpt,ypt])
		
file = '/Users/mcallister/projects/INP/land grids/land_grid_05x05.pckl'
with open(file,'w') as f:
    pickle.dump(land_list,f)


txo = [row[0] for row in plot_list]
tyo = [row[1] for row in plot_list]
#txol = [row[0] for row in land_list]
#tyol = [row[1] for row in land_list]
tests = m.scatter(txo,tyo)
#tests = m.scatter(txol,tyol,color = 'g')
plt.show()
