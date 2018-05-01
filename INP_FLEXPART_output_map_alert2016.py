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
parser.add_argument('-d','--traj_days', help='list the individual days (24hr periods) to plot from the trajectory', nargs='+', type=int)
args = parser.parse_args()


for sim_date in args.date_time: 
    base_path       ='/Volumes/storage/FLEXPART/Alert_2016/FLEXPART_2016_dkunkel/'
    hour_of_day     = PES.roundTime(sim_date,3600).hour
    sim_path        = os.path.join(base_path,str(sim_date.year) + str(sim_date.month).zfill(2)+ str(sim_date.day).zfill(2) + str(PES.roundValue(hour_of_day, 1)).zfill(2) + '0000/')
    print sim_path
    p_data          = glob.glob(sim_path+'summedPES*.h5')[0]
    p_nc_data       = glob.glob(sim_path+'grid_time_*.nc')[0]
    p_trajectory    = os.path.join(sim_path,'trajectories.txt')
    sim_date_start  = datetime(sim_date.year,sim_date.month,sim_date.day,PES.roundValue(hour_of_day, 1))
                       
    #define the figure
    fig = plt.figure(figsize=(10,10))

    #get the grid information
    xlat_i = PES.get_var(p_nc_data, 'latitude')
    xlon_i = PES.get_var(p_nc_data, 'longitude')

    xlon,xlat = np.meshgrid(xlon_i,xlat_i)
    pprint(xlat.shape)
    pprint(xlon.shape)

    #get the previously summed PES information
    Conc_var = PES.get_var(p_data, 'Conc_pCol100') #Conc_tCol Conc_pCol300
    print Conc_var.shape    

    #create a basemap instance
    m = Basemap(width=10000000,height=10000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.)

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
        traj_endpoints = PES.getTrajectoryMainz(p_trajectory)
        np_traj_endpoints = np.array(traj_endpoints)
        lats = np_traj_endpoints[:,0] 
        lons = np_traj_endpoints[:,1]
        xt,yt = m(lons,lats)
        bt = m.plot(xt,yt,color='k',linewidth=2,marker ='o')  

    #optional plot days along trajectory
    if args.traj_days is not None:
        params = {'mathtext.default': 'regular' }          
        plt.rcParams.update(params)
        traj_days = PES.getDaysOnTrajectoryMainz(p_trajectory, args.traj_days)
        print traj_days
        for day in traj_days:
            lat = day[0] 
            lon = day[1] 
            day = day[2] 
            xd,yd = m(lon,lat)
            db = m.plot(xd,yd,marker = 's',markerfacecolor='w',markersize=14)
            db = m.scatter(xd,yd,marker = r'${}$'.format(int(day)),zorder = 100,s=80)

  
    xs,ys = m(-62.355371,82.524010)
    m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)


    os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin')
    plt.savefig('FLEXPART_PES_0-100m_'+ sim_date_start.strftime("%Y%m%d-%H%M") + '_Alert.png', bbox_inches='tight', dpi=300)
    plt.show()
