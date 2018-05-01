#!/usr/bin/env python
# -- coding: UTF-8 --
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import os
import numpy as np                         
import matplotlib.pyplot as plt            
from mpl_toolkits.basemap import Basemap
import dateutil
from pprint import pprint
from datetime import datetime
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors  
import pandas as pd
from matplotlib import rc

# activate latex text rendering
rc('text', usetex=False)
#define the figure
fig, axes = plt.subplots(1,1,figsize=(10, 10))
                 
#create a basemap instance
m = Basemap(width=8000000,height=8000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.,rsphere=6378137.0)
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = '#084B8A', zorder = 0)
m.fillcontinents(color = '#D4BD8B', lake_color = '#084B8A', zorder=0)
m.drawcountries(zorder=300)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False],zorder=200)
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True],zorder=200)

#add measurements
prev_measurements_file = '/Users/mcallister/projects/INP/Alert_INP2016/docs/Previous Arctic measurements locations.csv'
df = pd.read_csv(prev_measurements_file)
#pprint(df)


m_colors = [
['g', 'o'],
['b', 's'],
['r', '<'],
['purple', '>'],
]


#sea ice and snow info
m.readshapefile('/Volumes/storage/NOAA snow and ice 4km-GEOtiff/ims2016071_4km_GIS_v1.3/ims2016071_4km_GIS_v1', 'surface_cover', drawbounds = False)
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



i=0
print '*** Ground stations ***'
for measurement in  df.loc[df['platform'] == 'Ground'].values.tolist():
	print measurement
	x,y = m(measurement[2],measurement[3])
	if measurement[0] == 'Radke et al., 1976':
		m.scatter(x,y+40000,marker = m_colors[i][1],s=200,zorder = 150, color = m_colors[i][0],label=measurement[0])
	elif measurement[0] == 'Fountain & Ohtake, 1985':
		m.scatter(x,y-70000,marker = m_colors[i][1],s=200,zorder = 150, color = m_colors[i][0],label=measurement[0])
	else:
		m.scatter(x,y,marker = m_colors[i][1],s=200,zorder = 150, color = m_colors[i][0],label=measurement[0])
	i+=1


#add arctic circle
arc_circle = []
for lon in np.arange(-180,180):
	lat = 66.56083
	arc_circle.append([lon,lat])
xc,yc = m([row[0] for row in arc_circle],[row[1] for row in arc_circle])
m.plot(xc,yc,marker = 'None', color = 'k',linewidth=1.5,linestyle='--',zorder=200)



lgd = plt.legend(loc=2,scatterpoints = 1)
lgd.set_zorder(300)  # put the legend on top

os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/prev_measurements/')
plt.savefig('AlertINP_prev_measurements_gr_stations.png', bbox_inches='tight', dpi=300)
plt.show()

