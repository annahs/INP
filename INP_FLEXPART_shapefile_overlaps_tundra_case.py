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
import pickle


sampling_times = [
#'2014-07-14  12:51:00',
#'2014-07-15  17:33:00',
#'2014-07-16  21:52:00',
#'2014-07-17  19:29:00',
#'2014-07-18  20:37:00',
#'2014-07-19  16:18:00',
#'2014-07-21  14:21:00',
'2014-07-23  14:41:00',
'2014-07-24  21:48:00',
'2014-07-25  19:50:00',
'2014-07-26  17:13:00',
'2014-07-27  17:47:00',
'2014-07-28  22:08:00',
'2014-07-29  13:40:00',
'2014-07-30  19:59:00',
'2014-07-31  17:15:00',
'2014-08-01  16:44:00',
'2014-08-02  20:03:00',
'2014-08-03  12:41:00',
'2014-08-04  14:57:00',
'2014-08-05  22:47:00',
'2014-08-07  12:50:00',
'2014-08-08  14:22:00',
'2014-08-09  14:10:00',
'2014-08-10  16:27:00',
'2014-08-11  14:07:00',
'2014-08-12  14:11:00',
]

months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names


for date in sampling_times:
    sim_date = PES.valid_date(date)
    base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
    minute_of_day   = sim_date.hour*60 + sim_date.minute
    output_path     = os.path.join(base_path,'ship-' + str(sim_date.day).zfill(2) + months[sim_date.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
    print output_path
    p_header        = os.path.join(output_path ,'header_d01.nc')
    p_data          = glob.glob(output_path+'summedPES*.h5')[0]
    p_trajectory    = os.path.join(output_path,'trajectories.txt')
     
    #get simulation dates and length
    sim_start_date = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')))
    sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
    sim_end_date   = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_END_DATE')))
    simulation_length = sim_start_date - sim_end_date
    day_of_year = sim_start_date.timetuple().tm_yday

    #get the grid information
    xlat = PES.get_var(p_header, 'XLAT')
    xlon = PES.get_var(p_header, 'XLONG')

    #create output array
    land_grid  = np.full_like(xlon, np.nan)

    #get the previously summed PES information
    Conc_var = PES.get_var(p_data, 'Conc_pCol300') #Conc_tCol Conc_pCol300
                           
    #create a basemap instance
    m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)

    #sea ice and snow info
    m.readshapefile('/Users/mcallister/projects/INP/mixedTundra_S_gt_p5_shp/mixedTundra_S_gt_p5_shp_WGS84', 'surface_cover', drawbounds = False)

    start = datetime.now()
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

            data = Conc_var[row][col]
            if data > 0:    
                if row % 10 == 0 and col % 10 == 0:
                    print row,col
                
                cell_vertices   = np.array([m(lon_0,lat_0),m(lon_1,lat_1),m(lon_2,lat_2),m(lon_3,lat_3)])
                cell_poly       = _geoslib.Polygon(cell_vertices)
                 
                #tundra
                fraction = 0
                for info, shape in zip(m.surface_cover_info, m.surface_cover):
                	#print info
                    if info['DN'] == 1 and info['RINGNUM'] == 1:
                        patch = Polygon(np.array(shape), True)
                        poly  = _geoslib.Polygon(patch.get_path().vertices)
                        fraction, intersection_poly = INP.calcPolygonOverlapArea(cell_poly, poly,fraction)
                        if fraction >= 1:
                            break
                
                land_grid[row][col]  = max(0,fraction)
               

    with open(os.path.join(output_path, 'gridded_fraction_tundra-'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.pckl'), 'wb') as file:
        pickle.dump(land_grid, file)

    print datetime.now() - start


