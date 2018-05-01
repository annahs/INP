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


parser = argparse.ArgumentParser(description='''
    calculates overlaps of PES cells in FLEXPART output with shapefiles for sea ice, land, and snow cover
  ''')
parser.add_argument('date_time',  help ='date and time of interest',type=PES.valid_date)
args = parser.parse_args()

months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names
base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
minute_of_day   = args.date_time.hour*60 + args.date_time.minute
output_path     = os.path.join(base_path,'ship-' + str(args.date_time.day).zfill(2) + months[args.date_time.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
print output_path
p_header        = os.path.join(output_path ,'header_d01.nc')
p_data          = glob.glob(output_path+'summedPES*.h5')[0]
 
#define the figure
fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')

#get simulation dates and length
sim_start_date = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')))
sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
sim_end_date   = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_END_DATE')))
simulation_length = sim_start_date - sim_end_date
day_of_year = sim_start_date.timetuple().tm_yday
                    
#create a basemap instance
m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = '#084B8A', zorder = 0)
m.fillcontinents(color = '#D4BD8B', lake_color = '#084B8A', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#sea ice and snow info
m.readshapefile('/Users/mcallister/projects/INP/NOAA snow and ice 4km-GEOtiff/ims2014195_4km_GIS_v1.2/test/test_WGS84', 'surface_cover', drawbounds = False)

#snow
i = 0
patches   = []
for info, shape in zip(m.surface_cover_info, m.surface_cover):    
    if info['DN'] ==4 and info['RINGNUM'] ==1:
        patches.append(Polygon(np.array(shape), True) )
        i+=1
axes.add_collection(PatchCollection(patches, facecolor= 'w', edgecolor='k', alpha = 1))

#sea ice
i = 0
patches   = []
for info, shape in zip(m.surface_cover_info, m.surface_cover):    
    if info['DN'] ==3 and info['RINGNUM'] ==1:
        patches.append(Polygon(np.array(shape), True) )
        i+=1
axes.add_collection(PatchCollection(patches, facecolor= '#CEE3F6', edgecolor='k', alpha = 1,zorder=-1))


all_lon_lats = {
datetime(2014,7,14):[-61.08522,    67.24028167],
datetime(2014,7,17):[-79.46350167, 73.98176167],
datetime(2014,7,23):[-94.52628333, 74.546745],
datetime(2014,7,27):[-63.62258833, 73.27793167],
datetime(2014,7,28):[-57.8847, 73.2611],
datetime(2014,7,29):[-61.61041833, 75.401505],
datetime(2014,7,30):[-71.2047, 76.33208167],
datetime(2014,8,9):[-98.50745833, 74.420585],
datetime(2014,8,10):[-96.23453333, 72.92619167],
datetime(2014,8,12):[-105.472, 68.97051333],

datetime(2014,7,18):[-81.018,73.5759],
datetime(2014,7,24):[-94.912, 74.6206],
}

lon = all_lon_lats[datetime(2014,sim_start_datetime.month,sim_start_datetime.day)][0]
lat = all_lon_lats[datetime(2014,sim_start_datetime.month,sim_start_datetime.day)][1]

xs,ys = m(lon,lat)
m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)


os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/')
plt.savefig('FLEXPART-WRF_landcover_'+ sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png', bbox_inches='tight', dpi=300)
plt.show()

