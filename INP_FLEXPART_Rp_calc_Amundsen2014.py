#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import os
import numpy as np                         
import matplotlib.pyplot as plt            
from matplotlib import cm                  
import matplotlib.colors as mcolors         
from mpl_toolkits.basemap import Basemap  
import h5py 
import FLEXPART_PES_NETCARE_module as PES
import INP_source_apportionment_module as INP 
from dateutil import parser
import argparse
import glob
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import numpy.ma as ma
import Alert_sampling_times as AL


all_datetimes = [
'2014 14th July 12:51',
'2014 15th July 17:33',
'2014 16th July 21:52',
'2014 17th July 19:29',
'2014 18th July 20:37',
'2014 19th July 16:18',
'2014 21st July 14:21',
#'2014 22nd July 12:23',
'2014 23rd July 14:41',
'2014 24th July 21:48',
'2014 25th July 19:50',
'2014 26th July 17:13',
'2014 27th July 17:47',
'2014 28th July 22:08',
'2014 29th July 13:40',
'2014 30th July 19:59',
'2014 31st July 17:15',
'2014 1st August  16:44',
'2014 2nd August  20:03',
'2014 3rd August  12:41',
'2014 4th August  14:57',
'2014 5th August  22:47',
'2014 7th August  12:50',
'2014 8th August  14:22',
'2014 9th August  14:10',
'2014 10th August  16:27',
'2014 11th August  14:07',
'2014 12th August  14:11',
]


top_36p_datetimes = ['20140718-2037','20140724-2148','20140721-1421','20140725-1950','20140726-1713','20140801-1644','20140803-1241','20140808-1422','20140811-1407']
bot_36p_datetimes = ['20140714-1251','20140717-1929','20140723-1441','20140727-1747','20140728-2208','20140729-1340','20140730-1959','20140809-1410','20140810-1627','20140812-1411']


base_path = '/Volumes/storage/FLEXPART/Amundsen_2014/FLEXPART-WRF/'

def avgPES(datetime_list,base_path):
	months = {7:'July',8:'Aug'}			#needed due to non-standard month formatting in file names
	print '***'
	summed_conc = []
	for sample_date_time in datetime_list:
		date_time = parser.parse(sample_date_time)
		#get the data and header paths
		minute_of_day   = date_time.hour*60 + date_time.minute
		output_path		= os.path.join(base_path,'ship-' + str(date_time.day).zfill(2) + months[date_time.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
		print output_path
		p_header        = os.path.join(output_path ,'header_d01.nc')
		p_data          = glob.glob(output_path+'summedPES*.h5')[0]
		#get the grid information
		xlat = PES.get_var(p_header, 'XLAT')
		xlon = PES.get_var(p_header, 'XLONG')
		#get the previously summed PES information
		Conc_var = PES.get_var(p_data, 'Conc_pCol300') #Conc_tCol Conc_pCol300	
		#append to the list of the concentration fields
		summed_conc.append(Conc_var)

	avgd_PES = np.mean(np.array(summed_conc), axis=0 )

	return avgd_PES


all_samples_PESavg = avgPES(all_datetimes,base_path)
all_samples_PESavg_masked = ma.masked_less(all_samples_PESavg, 0.005)

top36p_samples_PESavg = avgPES(top_36p_datetimes,base_path)
bot36p_samples_PESavg = avgPES(bot_36p_datetimes,base_path)

Rp_PES_top = np.divide(top36p_samples_PESavg,all_samples_PESavg_masked)*(len(top_36p_datetimes)*1.0/len(all_datetimes))
Rp_PES_bot = np.divide(bot36p_samples_PESavg,all_samples_PESavg_masked)*(len(bot_36p_datetimes)*1.0/len(all_datetimes))


print 'top: ', np.nanmin(Rp_PES_top), np.nanmax(Rp_PES_top), len(top_36p_datetimes),len(all_datetimes)
print 'bottom: ', np.nanmin(Rp_PES_bot), np.nanmax(Rp_PES_bot),len(bot_36p_datetimes),len(all_datetimes)


#create a basemap instance
m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)

#re-project the FLEXPART grid
p_header = os.path.join('/Volumes/storage/FLEXPART/Amundsen_2014/FLEXPART-WRF/ship-14July-backward/output_00501/' ,'header_d01.nc')
xlat = PES.get_var(p_header, 'XLAT')
xlon = PES.get_var(p_header, 'XLONG')
x,y=m(xlon,xlat)

#draw the map details
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = 'w', zorder = 0)
m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

ship_locations = {
	parser.parse('20140714-1251'):['zero',-61.08522,67.24028167],
	parser.parse('20140717-1929'):['zero',-79.46350167,73.98176167],
	parser.parse('20140723-1441'):['zero',-94.52628333,74.546745],
	parser.parse('20140727-1747'):['zero',-63.62258833,73.27793167],
	parser.parse('20140728-2208'):['zero',-57.8847,73.2611],
	parser.parse('20140729-1340'):['zero',-61.61041833,75.401505],
	parser.parse('20140730-1959'):['zero',-71.2047,76.33208167],
	parser.parse('20140809-1410'):['zero',-98.50745833,74.420585],
	parser.parse('20140810-1627'):['zero',-96.23453333,72.92619167],
	parser.parse('20140812-1411'):['zero',-105.472,68.97051333],}
for date_time in ship_locations:
	lon = ship_locations[date_time][1]
	lat = ship_locations[date_time][2]
	xs,ys = m(lon,lat) 
	m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)


###PES plot
levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
cols=PES.makeColormap(color_list)
norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
cs = m.contourf(x,y,bot36p_samples_PESavg, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES


##RP plot
#levels = np.arange(0,1.1,0.1)
##color_list = ['#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819']
#color_list = ['w','#ffffcc','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']
#cols=PES.makeColormap(color_list)
#norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
#cs = m.contourf(x,y,Rp_PES_bot, levels=levels, cmap=cols,  norm=norm) 

##add a color bar
cbar=plt.colorbar(cs, format="%.2f", orientation="vertical",fraction=.06, pad=0.08)
cbar.set_label('FLEXPART-WRF Residence Time (s)')



os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/Rp_plots/')
plt.savefig('FLEXPART-WRF_PES_0-300m_PES_bottom36pINP.png', bbox_inches='tight', dpi=300)
plt.show()







#20140714-1251 20140717-1929 20140723-1441 20140727-1747 20140728-2208 20140729-1340 20140730-1959 20140809-1410 20140810-1627 20140812-1411 20140718-2037 20140724-2148 20140715-1733 20140716-2152 20140719-1618 20140721-1421 20140725-1950 20140726-1713 20140731-1715 20140801-1644 20140802-2003 20140803-1241 20140804-1457 20140805-2247 20140807-1250 20140808-1422 20140811-1407  
#20140714-1251 20140717-1929 20140723-1441 20140727-1747 20140728-2208 20140729-1340 20140730-1959 20140809-1410 20140810-1627 20140812-1411 
#20140718-2037 20140724-2148

#top and bottom 36p
#20140718-2037 20140724-2148 20140721-1421 20140725-1950 20140726-1713 20140801-1644 20140803-1241 20140808-1422 20140811-1407  
#20140714-1251 20140717-1929 20140723-1441 20140727-1747 20140728-2208 20140729-1340 20140730-1959 20140809-1410 20140810-1627 20140812-1411 

#top and bottom 50p
#20140718-2037 20140724-2148 20140721-1421 20140725-1950 20140726-1713 20140801-1644 20140803-1241 20140808-1422 20140811-1407 20140719-1618 20140802-2003 20140805-2247 20140807-1250
#20140714-1251 20140717-1929 20140723-1441 20140727-1747 20140728-2208 20140729-1340 20140730-1959 20140809-1410 20140810-1627 20140812-1411 20140715-1733 20140716-2152 20140731-1715 20140804-1457

