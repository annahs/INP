#!/usr/bin/env python
# -- coding: UTF-8 --
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import os
import numpy as np                         
import matplotlib.pyplot as plt            
from mpl_toolkits.basemap import Basemap, _geoslib
import FLEXPART_PES_NETCARE_module as PES
import INP_source_apportionment_module as INP 
import dateutil
import argparse
import glob
from pprint import pprint
from datetime import datetime
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors         


#from osgeo import osr, gdal
#
## Read the data and metadata
#filename = '/Users/mcallister/projects/INP/glccgbe20_tif/gbbatsgeo20.tif'
#ds = gdal.Open(filename)
#
#data = ds.ReadAsArray()
#gt = ds.GetGeoTransform()
#proj = ds.GetProjection()
#print proj


#define the figure
fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
                 
#create a basemap instance
m = Basemap(width=12000000,height=12000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.)
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = '#084B8A', zorder = 0)
m.fillcontinents(color = '#D4BD8B', lake_color = '#084B8A', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#sea ice and snow info
m.readshapefile('/Volumes/storage/NOAA snow and ice 4km-GEOtiff/ims2016071_4km_GIS_v1.3/ims2016071_4km_GIS_v1', 'surface_cover', drawbounds = False)
print 'sea ice and snow shapefile read'
#read land cover data
#m.readshapefile('/Volumes/storage/glccgbe20_tif/gbbatsgeo20/gbbatsgeo20', 'surface_type', drawbounds = False)
#print 'land cover shapefile read'
print 'now to add snow and sea ice'
#snow
i = 0
patches   = []
for info, shape in zip(m.surface_cover_info, m.surface_cover):    
    if info['DN'] ==4 and info['RINGNUM'] ==1:
        patches.append(Polygon(np.array(shape), True) )
        i+=1
axes.add_collection(PatchCollection(patches, facecolor= 'w', edgecolor='k', alpha = 1,zorder=20))

#sea ice
i = 0
patches   = []
for info, shape in zip(m.surface_cover_info, m.surface_cover):    
    if info['DN'] ==3 and info['RINGNUM'] ==1:
        patches.append(Polygon(np.array(shape), True) )
        i+=1
axes.add_collection(PatchCollection(patches, facecolor= '#CEE3F6', edgecolor='k', alpha = 1,zorder=-1))
print 'sea ice in'

##surface type
#i = 0
#patches   = []
#for info, shape in zip(m.surface_type, m.surface_type): 
#	print info
#	if info['DN'] == 8: # and info['RINGNUM'] ==1:
#		patches.append(Polygon(np.array(shape), True) )
#		i+=1
#axes.add_collection(PatchCollection(patches, facecolor= 'red', edgecolor='k', alpha = 1,zorder=100))

xs,ys = m(-62.382840,82.500401)
m.scatter(xs,ys,marker = '*',zorder = 100, color = 'r', s=275)

#deserts
desert_names, desert_patches = INP.getDesertShapes(m)
patch_coll_d = PatchCollection(desert_patches,facecolor = '#bf8040',edgecolor='#362D0C',alpha = 1,zorder = 10)
deserts = axes.add_collection(patch_coll_d)

os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/landcover')
plt.savefig('FLEXPART-WRF_landcover_2016071_AlertINP.png', bbox_inches='tight', dpi=300)
plt.show()

