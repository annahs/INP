import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import os
import sys
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
from dateutil import parser
import math
from matplotlib.colors import LinearSegmentedColormap
import INP_source_apportionment_module as INPmod


location	 			= 'Inuvik'
day_to_plot 			= 20				#Alert 	7,8,9  Eureka 11,13  Inuvik 20, 21
sample_no 				= 1				#Alert 7-5, 8-4, 9-3  Eureka 11-4, 13-4  Inuvik 20-45, 21-4
include_arctic_circle 	= False
include_fires			= True
fire_threshold			= 80.
include_sea_ice			= False
max_ice_day				= 103 #Inuvik 103 (april 13)
overlay_enpoints		= False
bt_length 				= 10
boundary_layer			= True
include_trajectories	= True
overlay_enpoints		= False
save_fig				= True
nx, ny 					= 180,90. 			#grid

#### set up the basemap instance  	
sample_date = datetime(2015,4,day_to_plot)
#m = Basemap(width=15000000,height=11000000,
#            rsphere=(6378137.00,6356752.3142),\
#            resolution='l',area_thresh=1000.,projection='lcc',\
#            lat_1=45.,lat_2=55,lat_0=50,lon_0=-90.)
m = Basemap(projection='npstere',boundinglat=30,lon_0=270,resolution='l')

fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')
m.drawcoastlines()
#m.drawcountries()
parallels = np.arange(0.,81,10.)
m.drawparallels(parallels,labels=[False,True,False,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[False,False,False,True])



file_location = '/Users/mcallister/projects/INP_Meng/trajectories/'+ location +' 10d/sample'+ str(day_to_plot) +'_'+ str(sample_no) + 'w_ens_fwd'
file_position = 14

endpoints = INPmod.parseTrajectories(location,day_to_plot,sample_no,boundary_layer,file_location, file_position)


#### trajectory heatmap
#get gridded data
total_endpoints = len(endpoints)
np_endpoints = np.array(endpoints)
lats = np_endpoints[:,0] 
lons = np_endpoints[:,1]
heights = np_endpoints[:,2]
xs,ys,density_trajs,max_density = INPmod.getGriddedData(nx,ny,lats,lons,m)

#make colormap and color bar
my_cmap = INPmod.makeColormap('#e6eeff','#0055ff','#001a4d',max_density)
tick_pts = range(1,int(max_density),int(max_density/5))
tick_labels = []
for pt in tick_pts:
	label = round(pt*1.0/len(endpoints),3)
	tick_labels.append(label)


if include_trajectories == True:
	#do plotting
	mesh1 = plt.pcolormesh(xs, ys, density_trajs,vmin=0.01,cmap = my_cmap)
	cb1 = plt.colorbar(mesh1,ticks=tick_pts,orientation='horizontal')
	cb1.set_label('fraction of time in grid cell')
	cb1.ax.set_xticklabels(tick_labels)  # horizontal colorbar

	##overlay the scatter points to see that the density is working as expected
	if overlay_enpoints == True:
		x,y = m(lons, lats)
		bt = m.scatter(x,y, c=heights, cmap=plt.get_cmap('jet'),vmin = 0, vmax = 8000, edgecolors='none', marker = 'o',s=6)#,norm=matplotlib.colors.LogNorm())
		cb2 = plt.colorbar(bt,orientation='horizontal')
		cb2.set_label('alt (m)')


#### add fires
patches = []
if include_fires == True:
	MODIS_fires = INPmod.getMODISFires(sample_date,fire_threshold,bt_length)

	for fire in MODIS_fires:
		acq_date_time 	= fire[0]
		lat 			= fire[1]
		lon 			= fire[2]
		scan 			= fire[3]
		track 			= fire[4]
		x,y = m(lon,lat)
		#fires = m.scatter(x,y, s = 6, color = 'r')

		x1,y1 = (x-500*scan),(y-500*track)
		x2,y2 = (x-500*scan),(y+500*track)
		x3,y3 = (x+500*scan),(y+500*track)	
		x4,y4 = (x+500*scan),(y-500*track)
		p = Polygon([(x1,y1),(x2,y2),(x3,y3),(x4,y4)]) 
		#axes.add_patch(p)
		patches.append(p)


	

	#### calc overlap for fires and enpoints
	#plot a density map of fire points that is on the same grid as the endpoints
	#multiply the values of each cell, if no enpoints or fires value is 0, else value is #hours x #fires in units of hours
	lats_f = [row[1] for row in MODIS_fires]
	lons_f = [row[2] for row in MODIS_fires]
	xs2,ys2,density_fires,max_density2 = INPmod.getGriddedData(nx,ny,lats_f,lons_f,m)
	
	#zip together the density maps for the fires and endpoints
	fire_overlap = [a*b for a,b in zip(density_trajs,density_fires)]
	print 'hours*fires ',np.sum(fire_overlap)/total_endpoints
	patch_coll = PatchCollection(patches,facecolor = '#ff531a',edgecolor='#ff531a')
	axes.add_collection(patch_coll)







#### add text


#### save
os.chdir('/Users/mcallister/projects/INP_Meng/')

if save_fig == True:
	bl = ''
	if boundary_layer == True:
		bl = '_inPBL'
	plt.text(0.0, 1.025,'April '+ str(day_to_plot) + ', sample ' + str(sample_no) + ', ' + bl, fontsize = 14,transform=axes.transAxes)
	plt.savefig('fwd_'+location + '_' + str(day_to_plot) +'-'+ str(sample_no)  + '_' + bl +'.pdf',format = 'pdf', bbox_inches='tight') 

plt.show()