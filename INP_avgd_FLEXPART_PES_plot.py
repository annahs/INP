#!/usr/bin/env python
# -- coding: UTF-8 --
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
import dateutil
import argparse
import glob
from pprint import pprint
from datetime import datetime
from datetime import timedelta


parser = argparse.ArgumentParser(description='''
    Creates an averaged stereographic projection of FLEXPART PES output from a sepcified set of HDF5 files
  ''')
parser.add_argument('-d','--date_times', help='list the individual dates and times of interest', nargs='+', type=PES.valid_date)
parser.add_argument('-f','--add_fires', help='plot fires within the simulation period', action='store_true')
parser.add_argument('-s','--add_ship_posns', help='plot ship positions', action='store_true')
args = parser.parse_args()

base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
months = {7:'July',8:'Aug'}			#needed due to non-standard month formatting in file names

summed_conc = []
for date_time in args.date_times:
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


#create a basemap instance
m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)

#re-project the FLEXPART grid
x,y=m(xlon,xlat)

#draw the map details
m.drawcoastlines(linewidth=0.5)
m.drawmapboundary(fill_color = 'w', zorder = 0)
m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#make the PES contour plot 
levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
cols=PES.makeColormap(color_list)
norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
cs = m.contourf(x,y,avgd_PES, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

#add a scale bar
#cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
#cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
#cbar.set_label('FLEXPART-WRF residence time (s)')

#optional add fires
if args.add_fires:
	MODIS_file      = 'fire_archive_M6_8493-MOSSI2014.txt' 
	fire_threshold  = 80
	sim_start_date = max(args.date_times)
	simulation_length = max(args.date_times) - min(args.date_times) + timedelta(days=7) 
	print sim_start_date, simulation_length, max(args.date_times), min(args.date_times)
	fire_list   = INP.getMODISFires(sim_start_date,fire_threshold,simulation_length.days,MODIS_file,min_lat=40, min_lon = -170, max_lon = 10)
	lons        = [row[2] for row in fire_list]
	lats        = [row[1] for row in fire_list]
	frp         = [row[5] for row in fire_list]
	frp_size    = [INP.mapValue(row[5],  min(frp), max(frp), 8, 80) for row in fire_list]
	xf,yf       = m(lons,lats)         

	fp = m.scatter(xf,yf,marker = 'o',zorder = 100,s=frp_size,facecolor = 'm', edgecolor = 'k', linewidth='0.5')

if args.add_ship_posns:
	ship_locations = {
	dateutil.parser.parse('20140714-1251'):['zero',-61.08522,67.24028167],
	dateutil.parser.parse('20140717-1929'):['zero',-79.46350167,73.98176167],
	dateutil.parser.parse('20140723-1441'):['zero',-94.52628333,74.546745],
	dateutil.parser.parse('20140727-1747'):['zero',-63.62258833,73.27793167],
	dateutil.parser.parse('20140728-2208'):['zero',-57.8847,73.2611],
	dateutil.parser.parse('20140729-1340'):['zero',-61.61041833,75.401505],
	dateutil.parser.parse('20140730-1959'):['zero',-71.2047,76.33208167],
	dateutil.parser.parse('20140809-1410'):['zero',-98.50745833,74.420585],
	dateutil.parser.parse('20140810-1627'):['zero',-96.23453333,72.92619167],
	dateutil.parser.parse('20140812-1411'):['zero',-105.472,68.97051333],

	dateutil.parser.parse('20140718-2037'):['high',-81.01786,73.56860833],
	dateutil.parser.parse('20140724-2148'):['high',-94.9116,74.6204],
	dateutil.parser.parse('20140715-1733'):['other',-64.8471,69.3589],
	dateutil.parser.parse('20140716-2152'):['other',-71.11666,71.70185167],
	dateutil.parser.parse('20140719-1618'):['other',-83.97575,74.11009],
	dateutil.parser.parse('20140721-1421'):['other',-92.2254,74.2369],
	dateutil.parser.parse('20140725-1950'):['other',-86.99806333,74.42822667],
	dateutil.parser.parse('20140726-1713'):['other',-75.27019167,73.92597333],
	dateutil.parser.parse('20140731-1715'):['other',-73.27239833,76.3168],
	dateutil.parser.parse('20140801-1644'):['other',-76.09716,76.339745],
	dateutil.parser.parse('20140802-2003'):['other',-72.68896667,78.93360833],
	dateutil.parser.parse('20140803-1241'):['other',-64.17983833,81.36700833],
	dateutil.parser.parse('20140804-1457'):['other',-69.293165,80.131075],
	dateutil.parser.parse('20140805-2247'):['other',-71.68982833,79.0777],
	dateutil.parser.parse('20140807-1250'):['other',-78.38091833,74.700675],
	dateutil.parser.parse('20140808-1422'):['other',-96.15090167,74.19084667],
	dateutil.parser.parse('20140811-1407'):['other',-99.24270667,70.09025167],
	}

	for date_time in args.date_times:
		lon = ship_locations[date_time][1]
		lat = ship_locations[date_time][2]
		xs,ys = m(lon,lat) 
		m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)
		desc = 'all_'#ship_locations[date_time][0]

os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/')
plt.savefig('FLEXPART-WRF_PES_0-300m_'+ desc +'INPavg_AmundsenINP_noCB_nofires.png', bbox_inches='tight', dpi=300)
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

