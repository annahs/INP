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

parser = argparse.ArgumentParser(description='''
    calculates overlaps of PES cells in FLEXPART output with shapefiles for sea ice, land, and snow cover
  ''')
parser.add_argument('date_time',  help ='date(s) and time(s) of interest',nargs='+',type=PES.valid_date)
parser.add_argument('-g','--add_grid', help='plot the grid', action='store_true')
parser.add_argument('-p','--add_PES',  help='plot the PES', action='store_true')
parser.add_argument('-s','--add_ship',  help='plot the ships position', action='store_true')
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

    #create output arrays
    bare_land_grid  = np.full_like(xlon, np.nan)
    snow_cover_grid = np.full_like(xlon, np.nan)
    sea_ice_grid    = np.full_like(xlon, np.nan)
    open_ocean_grid = np.full_like(xlon, np.nan)

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

    #sea ice and snow info
    m.readshapefile('/Users/mcallister/projects/INP/NOAA snow and ice 4km-GEOtiff/ims2014'+ str(day_of_year) + '_4km_GIS_v1.2/ims2014'+ str(day_of_year) + '_4km_shp/ims2014'+ str(day_of_year) + '_4km_shp_WGS84', 'surface_cover', drawbounds = False)

    sn_test_list = []
    si_test_list = []
    grid_polygons = []
    land_test_list = []

    bare_land_parameter  = 0.
    si_parameter    = 0.
    sn_parameter    = 0.
    open_ocean_parameter = 0.


    start = datetime.now()
    for indx, val in np.ndenumerate(xlon):

        row = indx[0]
        col = indx[1]

        if (0 <= row < 398) and (0 <= col < 398): 
            
            data = Conc_var[row][col]

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

            if data > 0:    
                if row % 10 == 0 and col % 10 == 0:
                    print row,col
                
                cell_vertices   = np.array([m(lon_0,lat_0),m(lon_1,lat_1),m(lon_2,lat_2),m(lon_3,lat_3)])
                cell_poly      = _geoslib.Polygon(cell_vertices)
                cell_area       = cell_poly.area()

                #land
                land_fraction = 0
                for land_polygon in m.landpolygons:
                    land_fraction, ln_intersection_poly = INP.calcPolygonOverlapArea(cell_poly, land_polygon,land_fraction)
                    if land_fraction >= 1:
                        break
                    #land_test_list.append(ln_intersection_poly)

                #sea ice
                si_fraction = 0
                for info, shape in zip(m.surface_cover_info, m.surface_cover):    
                    if info['DN'] ==3 and info['RINGNUM'] ==1:
                        si_patch = Polygon(np.array(shape), True)
                        si_poly  = _geoslib.Polygon(si_patch.get_path().vertices)
                        si_fraction, si_intersection_poly = INP.calcPolygonOverlapArea(cell_poly, si_poly,si_fraction)
                        if si_fraction >= 1:
                            break
                        #si_test_list.append(si_intersection_poly)


                #snow
                sn_fraction = 0
                for info, shape in zip(m.surface_cover_info, m.surface_cover):    
                    if info['DN'] ==4 and info['RINGNUM'] ==1:
                        sn_patch = Polygon(np.array(shape), True)
                        sn_poly  = _geoslib.Polygon(sn_patch.get_path().vertices)
                        sn_fraction, sn_intersection_poly = INP.calcPolygonOverlapArea(cell_poly, sn_poly,sn_fraction)
                        if sn_fraction >= 1:
                            break
                        #sn_test_list.append(sn_intersection_poly)

                if land_fraction == 1:
                    si_fraction = 0.
                open_ocean_fraction = 1.-land_fraction-si_fraction
                bare_land_fraction = land_fraction - sn_fraction

                bare_land_parameter     += data*max(0, bare_land_fraction) #set a zero minimum for each of these
                si_parameter            += data*max(0, si_fraction)
                sn_parameter            += data*max(0, sn_fraction)
                open_ocean_parameter    += data*max(0, open_ocean_fraction) 

                bare_land_grid[row][col]  = max(0, bare_land_fraction)
                snow_cover_grid[row][col] = max(0, sn_fraction)
                sea_ice_grid[row][col]    = max(0, si_fraction)
                open_ocean_grid[row][col] = max(0, open_ocean_fraction)

    print 'bare land', bare_land_parameter 
    print 'snow', sn_parameter  
    print 'sea ice', si_parameter   
    print 'open ocean', open_ocean_parameter

    with open(os.path.join(output_path , 'gridded_fraction_bare_land-'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.pckl'), 'wb') as file:
        pickle.dump(bare_land_grid, file)
    with open(os.path.join(output_path , 'gridded_fraction_snow_cover-'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.pckl'), 'wb') as file:
        pickle.dump(snow_cover_grid, file)
    with open(os.path.join(output_path , 'gridded_fraction_sea_ice-'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.pckl'), 'wb') as file:
        pickle.dump(sea_ice_grid,file)
    with open(os.path.join(output_path , 'gridded_fraction_open_ocean-'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.pckl'), 'wb') as file:
        pickle.dump(open_ocean_grid, file)


    #plot snow and sea ice coverage
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



    if args.add_grid == True:
        axes.add_collection(PatchCollection(grid_polygons, facecolor='none',edgecolor='k',alpha = 1,zorder=10))



    if args.add_PES == True:
        #re-project the FLEXPART grid
        x,y=m(xlon,xlat)
        #m.scatter(x,y,marker = 'o',zorder = 100, color = 'b', s=0.1)
        
        #make the PES contour plot 
        levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
        color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
        cols=PES.makeColormap(color_list)
        norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
        cs = m.contourf(x,y,Conc_var, levels=levels, cmap=cols,  norm=norm, zorder = -1,alpha = 0.1) 
        
        #add a scale bar
        cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
        cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
        cbar.set_label('FLEXPART-WRF total column residence time (s)')



    if args.add_ship == True:
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


    ###for testing
    #axes.add_collection(PatchCollection(sn_test_list,facecolor = 'blue',edgecolor='k',alpha = 0.1))
    #axes.add_collection(PatchCollection(si_test_list,facecolor = 'm',edgecolor='k',alpha = 0.1))
    #axes.add_collection(PatchCollection(land_test_list,facecolor = 'g',edgecolor='k',alpha = 0.1))

    print datetime.now() - start

    plt.savefig(os.path.join(output_path , 'snow_ice_cover_'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png'), bbox_inches='tight', dpi=300)
    #plt.show()

