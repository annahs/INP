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
import INP_source_apportionment_module as INPmod
from matplotlib.path import Path
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection




date = datetime(2016,3,25)
day_of_year = date.timetuple().tm_yday
print date,day_of_year
lat_pt = 39.5


###set up the basemap instance  
fig = plt.figure(figsize=(8,8))
ax = fig.add_subplot(111)
m = Basemap(projection='nplaea',boundinglat=35,lon_0=270,resolution='l')
m.drawmapboundary(fill_color='#084B8A')
m.fillcontinents(color='#D4BD8B',lake_color='#084B8A',zorder = -10)
m.drawcoastlines()
m.drawcountries()
parallels = np.arange(0.,81,10.)
m.drawparallels(parallels,labels=[False,False,False,False])
meridians = np.arange(10.,351.,60.)
m.drawmeridians(meridians,labels=[True,True,True,True])



#NSIDC ascii data
sea_ice, snow, sea_ice_pts = INPmod.getSeaIceAndSnow(m, date.year, day_of_year, resolution = 24)
si_patch_coll = PatchCollection(sea_ice,facecolor='#CEE3F6',edgecolor='#CEE3F6', alpha = 1.0)
sn_patch_coll = PatchCollection(snow,facecolor='w',edgecolor='w', alpha = 1.0)


#plottting
sea_ice_patches = ax.add_collection(si_patch_coll)		
snow_patches = ax.add_collection(sn_patch_coll)		
		
		
#BTs	
clusters = []
cluster_endpoints={}
for number in [1,2,3]:
	cluster_endpoints[number]=[]
	clusters.append(number)
	
with open('/Users/mcallister/projects/INP/Alert_INP2016/bin/working/CLUSLIST_3','r') as f:
	
	for line in f:
		newline = line.split()
		cluster = int(newline[0])
		file = newline[7]

		tdump_file = open(file, 'r')
		endpoints = []
		data_start = False

		i=0
		for line in tdump_file:
			newline = line.split()

			if data_start == True:
				lat = float(newline[9])
				lon = float(newline[10])
			
			
				endpoint = [lat, lon]
				endpoints.append(endpoint)
				i+=1
			if newline[1] == 'PRESSURE':
				data_start = True
			
			
		tdump_file.close() 
		
		cluster_endpoints[cluster].append(endpoints)
			
colors = ['b','orange','g','r','c','m','k','y','#DF7401','#585858','grey','#663300']

for cluster_no in clusters:
	list = cluster_endpoints[cluster_no]
	for row in list:
		np_endpoints = np.array(row)
		lats = np_endpoints[:,0] 
		lons = np_endpoints[:,1]
		x,y = m(lons,lats)
		bt = m.plot(x,y,color=colors[cluster_no],linewidth=2)
			

os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/SSI_clusters')
plt.savefig('ALERT_10day_backtrajectory_with_surface_cover_'+str(day_of_year)+'-Alert_SSI_March_2016.png', bbox_inches='tight') 


plt.show()
plt.clf()
plt.close(fig)
