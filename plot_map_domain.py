#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys   
reload(sys)  
sys.setdefaultencoding('utf8')   
import numpy as np                         
import matplotlib.pyplot as plt            
from matplotlib import cm                  
import matplotlib.colors as mcolors      
from matplotlib.patches import Polygon
from mpl_toolkits.basemap import Basemap  
from matplotlib.collections import PatchCollection
import h5py                                                             
import os 
import glob
from pprint import pprint
import calendar
import dateutil
import FLEXPART_PES_NETCARE_module as PES
import argparse

#File objects
#File objects serve as your entry point into the world of HDF5. In addition to the File-specific capabilities listed here, 
#every File instance is also an HDF5 group representing the root group of the file.

#Groups
#Each file begins with at least one group, the root group. Groups are the container mechanism by which HDF5 files are organized. 
#From a Python perspective, they operate somewhat like dictionaries. In this case the “keys” are the names of group members, and the “values” are 
#the members themselves (Group and Dataset) objects.

#datasets
#Datasets are very similar to NumPy arrays. They are homogenous collections of data elements, with an immutable datatype and (hyper)rectangular shape. 
#Unlike NumPy arrays, they support a variety of transparent storage features such as compression, error-detection, and chunked I/O.
#They are represented in h5py by a thin proxy class which supports familiar NumPy operations like slicing, along with a variety of descriptive attributes:
# -shape attribute
# -size attribute
# -dtype attribute

#Attributes	
#Attributes are a critical part of what makes HDF5 a “self-describing” format. They are small named pieces of data attached directly to Group and 
#Dataset objects. This is the official way to store metadata in HDF5.



n_header = 'header_d01.nc'  
dfolder  = '/Users/mcallister/projects/INP/FLEXPART-WRF/ship-14July-backward/output_00781/'
p_header = os.path.join(dfolder,n_header)

start_str,date_str,p_data = PES.getDataPathFromFilename(dfolder)

#create file objects
f_head = h5py.File(p_header, mode='r')
f_tracer = h5py.File(p_data, mode = 'r') 


##get info
#print f_head.name 								#shows as / i.e. root group
#pprint(f_head.keys())							#get dataset info, all in one group here - the root group
#print f_head['XLAT'].shape						#get dataset shape
#pprint(f_head['XLAT'].attrs.items())			#Get (name, value) tuples for all attributes attached to this object
#pprint((np.array(f_head['XLAT_CORNER'])))	#get dataset Attributes



### map grid 
fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
#m = Basemap(width=6700000,height=6700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)
m = Basemap(projection='ortho',lon_0=-83,lat_0=70,resolution='l')
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = '#084B8A', zorder = 0)
m.fillcontinents(color = '#D4BD8B', lake_color = '#084B8A', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,10.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#get the grid information
xlat = PES.get_var(p_header, 'XLAT')
xlon = PES.get_var(p_header, 'XLONG')

points = []
for indx, val in np.ndenumerate(xlon):

	row = indx[0]
	col = indx[1]

	if row == 0 or row == 398: 
		lon_0 = xlon[row][col]
		lat_0 = xlat[row][col]
		x,y = m(lon_0,lat_0)
		m.scatter(x,y,color='r',s = 10,zorder = 100)

	if col == 0 or col == 398: 
		lon_0 = xlon[row][col]
		lat_0 = xlat[row][col]
		x,y = m(lon_0,lat_0)
		m.scatter(x,y,color='r',s = 10,zorder = 100)

plt.savefig(('/Users/mcallister/projects/INP/FLEXPART-WRF/WRF_domain.png'), bbox_inches='tight', dpi=300)
plt.show()
