#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
import pickle

sampling_times = [
'2014-07-14  12:51:00',
#'2014-07-15  17:33:00',
#'2014-07-16  21:52:00',
#'2014-07-17  19:29:00',
#'2014-07-18  20:37:00',
#'2014-07-19  16:18:00',
#'2014-07-21  14:21:00',
#'2014-07-23  14:41:00',
#'2014-07-24  21:48:00',
#'2014-07-25  19:50:00',
#'2014-07-26  17:13:00',
#'2014-07-27  17:47:00',
#'2014-07-28  22:08:00',
#'2014-07-29  13:40:00',
#'2014-07-30  19:59:00',
#'2014-07-31  17:15:00',
#'2014-08-01  16:44:00',
#'2014-08-02  20:03:00',
#'2014-08-03  12:41:00',
#'2014-08-04  14:57:00',
#'2014-08-05  22:47:00',
#'2014-08-07  12:50:00',
#'2014-08-08  14:22:00',
#'2014-08-09  14:10:00',
#'2014-08-10  16:27:00',
#'2014-08-11  14:07:00',
#'2014-08-12  14:11:00',
]

plot_grid       = False
plot_PES        = True
plot_trajectory = False

months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names
for date in sampling_times:
    sim_date 		= PES.valid_date(date)    
    base_path       = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
    minute_of_day   = sim_date.hour*60 + sim_date.minute
    output_path     = os.path.join(base_path,'ship-' + str(sim_date.day).zfill(2) + months[sim_date.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
    print output_path
    p_header        = os.path.join(output_path ,'header_d01.nc')
    p_data          = glob.glob(output_path+'summedPES*.h5')[0]
    p_trajectory    = os.path.join(output_path,'trajectories.txt')
     
    #define the figure
    fig, axes = plt.subplots(1,1,figsize=(12, 10), facecolor='w', edgecolor='k')

    #get simulation dates and length
    sim_start_date = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')))
    sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
    sim_end_date   = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_END_DATE')))
    simulation_length = sim_start_date - sim_end_date
    day_of_year = sim_start_date.timetuple().tm_yday

    #get the grid information
    xlat = PES.get_var(p_header, 'XLAT')
    xlon = PES.get_var(p_header, 'XLONG')

    #get the previously summed PES information
    Conc_var = PES.get_var(p_data, 'Conc_pCol300') #Conc_tCol Conc_pCol300
                           
    #create a basemap instance
    m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)
    m.drawcoastlines(linewidth=0.5)
    m.drawmapboundary(fill_color = '#084B8A', zorder = 0)
    m.fillcontinents(color = '#D4BD8B', lake_color = '#084B8A', zorder=0)
    parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
    m.drawparallels(parallels,labels=[False,True,True,False])
    meridians = np.arange(10.,351.,20.)
    m.drawmeridians(meridians,labels=[True,False,False,True])


    if plot_trajectory == True:
        traj_endpoints = PES.getTrajectory(p_trajectory)
        np_traj_endpoints = np.array(traj_endpoints)
        lats = np_traj_endpoints[:,0] 
        lons = np_traj_endpoints[:,1]
        xt,yt = m(lons,lats)
        bt = m.plot(xt,yt,color='r',linewidth=2,zorder=200)

    if plot_PES == True: 
        x,y=m(xlon,xlat)
        levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
        levels = ([5])
        color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
        color_list = ['#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
        cols=plt.cm.binary#PES.makeColormap(color_list)
        norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
        #cs = m.contourf(x,y,Conc_var, levels=levels, cmap=cols, norm=norm, alpha =0.55 ,zorder=100) 
        cs = m.contour(x,y,Conc_var, levels=levels, colors ='r', linewidths = 2.0,zorder=101) 
    
        #cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
        #cbar.set_label('FLEXPART-WRF residence time (s)')


   
    if plot_grid == True:
        grid_polygons = []
        for indx, val in np.ndenumerate(xlon):

            row = indx[0]
            col = indx[1]

            if (0 <= row < 398) and (0 <= col < 398):     
                lon_0 = xlon[row][col]
                lon_1 = xlon[row][col+1]  
                lon_2 = xlon[row+1][col+1]
                lon_3 = xlon[row+1][col]

                lat_0 = xlat[row][col]
                lat_1 = xlat[row][col+1]  
                lat_2 = xlat[row+1][col+1]
                lat_3 = xlat[row+1][col]

                cell = Polygon([m(lon_0,lat_0),m(lon_1,lat_1),m(lon_2,lat_2),m(lon_3,lat_3)])
                grid_polygons.append(cell)
        axes.add_collection(PatchCollection(grid_polygons, facecolor='none',edgecolor='k',alpha = 1,zorder=10))

    
    #sea ice and snow info
    m.readshapefile('/Users/mcallister/projects/INP/NOAA snow and ice 4km-GEOtiff/ims2014'+ str(day_of_year) + '_4km_GIS_v1.2/ims2014'+ str(day_of_year) + '_4km_shp/ims2014'+ str(day_of_year) + '_4km_shp_WGS84', 'surface_cover', drawbounds = False)
    #tundra info
    m.readshapefile('/Users/mcallister/projects/INP/mixedTundra_S_gt_p5_shp/mixedTundra_S_gt_p5_shp_WGS84', 'tundra', drawbounds = False)


    #snow
    i = 0
    patches   = []
    for info, shape in zip(m.surface_cover_info, m.surface_cover):    
        if info['DN'] ==4 and info['RINGNUM'] ==1:
            patches.append(Polygon(np.array(shape), True) )
            i+=1
    axes.add_collection(PatchCollection(patches, facecolor= 'w', edgecolor='k', alpha = 0.5,zorder=2))

    #sea ice
    i = 0
    patches   = []
    for info, shape in zip(m.surface_cover_info, m.surface_cover):    
        if info['DN'] ==3 and info['RINGNUM'] ==1:
            patches.append(Polygon(np.array(shape), True) )
            i+=1
    axes.add_collection(PatchCollection(patches, facecolor= '#CEE3F6', edgecolor='k', alpha = 0.5,zorder=-1))

    #tundra
    i = 0
    patches   = []
    for info, shape in zip(m.tundra_info, m.tundra):    
        if info['DN'] == 1 and info['RINGNUM'] ==1:
            patches.append(Polygon(np.array(shape), True) )
            i+=1
    axes.add_collection(PatchCollection(patches, facecolor= '#229933', edgecolor='k', alpha = 0.5,zorder=1))


    #ship's position
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

    datetime(2014,7,15):[-64.8471,69.3589],
    datetime(2014,7,16):[-71.11666,71.70185167],
    datetime(2014,7,19):[-83.97575,74.11009],
    datetime(2014,7,21):[-92.2254,74.2369],
    datetime(2014,7,25):[-86.8667,74.43272833],
    datetime(2014,7,26):[-75.27019167,73.92597333],
    datetime(2014,7,31):[-73.27239833,76.3168],
    datetime(2014,8,1):[-76.09716,76.339745],
    datetime(2014,8,2):[-72.68896667,78.93360833],
    datetime(2014,8,3):[-64.17983833,81.36700833],
    datetime(2014,8,4):[-69.293165,80.131075],
    datetime(2014,8,5):[-71.68982833,79.0777],
    datetime(2014,8,7):[-78.38091833,74.700675],
    datetime(2014,8,8):[-96.15090167,74.19084667],
    datetime(2014,8,11):[-99.24270667,70.09025167],
    }

    lon = all_lon_lats[datetime(2014,sim_start_datetime.month,sim_start_datetime.day)][0]
    lat = all_lon_lats[datetime(2014,sim_start_datetime.month,sim_start_datetime.day)][1]

    xs,ys = m(lon,lat)
    m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'r', s=50)

    #plt.savefig(os.path.join('/Users/mcallister/projects/INP/FLEXPART-WRF/land_cover_PES_plots/' , 'snow_ice_tundra_cover_PES_trajectory'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png'), bbox_inches='tight', dpi=300)
    plt.show()
    plt.close()



