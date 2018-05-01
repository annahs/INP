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
import dateutil
import argparse
import glob
from pprint import pprint
from datetime import datetime


parser = argparse.ArgumentParser(description='''
    Creates a stereographic projection of FLEXPART output from HDF5 files created from Calculate_PES_NETCARE2014_shared.py (put these files in your working directory)
    Created on Wed Aug 31 13:30:52 2016
    @author: meganwillis
  ''')
parser.add_argument('date_time',  help ='date and time of interest',nargs='+',type=PES.valid_date)
parser.add_argument('-t','--add_trajectory', help='plot the trajectory', action='store_true')
parser.add_argument('-f','--add_fires', help='plot fires within the simulation period', action='store_true')
parser.add_argument('-d','--traj_days', help='list the individual days (24hr periods) to plot from the trajectory', nargs='+', type=int)
args = parser.parse_args()

for sim_date in args.date_time:
    months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names
    base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
    minute_of_day   = sim_date.hour*60 + sim_date.minute
    output_path     = os.path.join(base_path,'ship-' + str(sim_date.day).zfill(2) + months[sim_date.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
    print output_path
    p_header        = os.path.join(output_path ,'header_d01.nc')
    p_data          = glob.glob(output_path+'summedPES*.h5')[0]
    p_trajectory    = os.path.join(output_path,'trajectories.txt')

    MODIS_file      = 'fire_archive_M6_8493-MOSSI2014.txt' 
    fire_threshold  = 80
                       
    #define the figure
    fig = plt.figure(figsize=(10,10))

    #get simulation dates and length
    sim_start_date = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')))
    sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
    sim_end_date   = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_END_DATE')))
    simulation_length = sim_start_date - sim_end_date
    print sim_start_datetime

    #get the grid information
    xlat = PES.get_var(p_header, 'XLAT')
    xlon = PES.get_var(p_header, 'XLONG')

    pprint(xlat)
    pprint(xlat.shape)
    #print xlon[0]
    #sys.exit()

    #get the previously summed PES information
    Conc_var = PES.get_var(p_data, 'Conc_pCol300') #Conc_tCol Conc_pCol300
                           
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
    cs = m.contourf(x,y,Conc_var, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

    #add a scale bar
    #cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
    cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
    cbar.set_label('FLEXPART-WRF residence time (s)')

    ##optional add trajectory
    if args.add_trajectory:
        traj_endpoints = PES.getTrajectory(p_trajectory)
        np_traj_endpoints = np.array(traj_endpoints)
        lats = np_traj_endpoints[:,0] 
        lons = np_traj_endpoints[:,1]
        xt,yt = m(lons,lats)
        bt = m.plot(xt,yt,color='k',linewidth=2)  

    #optional plot days along trajectory
    if args.traj_days is not None:
        params = {'mathtext.default': 'regular' }          
        plt.rcParams.update(params)
        traj_days = PES.getDaysOnTrajectory(p_trajectory, args.traj_days)
        print traj_days
        for day in traj_days:
            lat = day[0] 
            lon = day[1] 
            day = day[2] 
            xd,yd = m(lon,lat)
            db = m.plot(xd,yd,marker = 's',markerfacecolor='w',markersize=14)
            db = m.scatter(xd,yd,marker = r'${}$'.format(int(day)),zorder = 100,s=80)

    #optional add fires
    if args.add_fires:
        fire_list   = INP.getMODISFires(sim_start_date,fire_threshold,simulation_length.days,MODIS_file)
        lons        = [row[2] for row in fire_list]
        lats        = [row[1] for row in fire_list]
        frp         = [row[5] for row in fire_list]
        frp_size    = [INP.mapValue(row[5],  min(frp), max(frp), 8, 80) for row in fire_list]
        xf,yf       = m(lons,lats)         

        fp = m.scatter(xf,yf,marker = 'o',zorder = 100,s=frp_size,facecolor = 'm', edgecolor = 'k', linewidth='0.5')

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
    m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)


    os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/')
    plt.savefig('FLEXPART-WRF_PES_0-300m_'+ sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png', bbox_inches='tight', dpi=300)
    #plt.show()
