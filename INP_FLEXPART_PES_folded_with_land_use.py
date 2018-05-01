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
import pickle
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcol



def openLandParameters(file):
	pkl_file = open(file, 'rb')
	parameter_grid = pickle.load(pkl_file)
	pkl_file.close()

	return parameter_grid

def makeMap(axes):
	#create a basemap instance
	m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.,ax = axes)
	m.drawcoastlines(linewidth=0.5)
	m.drawmapboundary(fill_color = 'none', zorder = 2)
	#m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
	parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
	m.drawparallels(parallels,labels=[False,False,False,False])
	meridians = np.arange(10.,351.,20.)
	m.drawmeridians(meridians,labels=[False,False,False,False])

	return m


parser = argparse.ArgumentParser(description='''
    calculates overlaps of PES cells in FLEXPART output with shapefiles for sea ice, land, and snow cover
  ''')
parser.add_argument('date_time',  help ='date(s) and time(s) of interest',nargs='+',type=PES.valid_date)
parser.add_argument('-s','--save_params',  help='save parameters to file', action='store_true')
args = parser.parse_args()



if args.save_params == True:
	p_file = '/Users/mcallister/projects/INP/FLEXPART-WRF/FLEXPART-WRF_PES_surface_cover_parameters_AMUNDSEN_2014-t.txt'
	#delete if the file exists
	try:
	    os.remove(p_file)
	except OSError:
	    pass
	with open(p_file,'w') as pf:
		pf.write('date_time' + '\t'  +  'bare_land_parameter' +  '\t' + 'norm_bare_land_parameter' +  '\t' +  'tundra_er05_parameter' +  '\t' + 'norm_tundra_er05_parameter' +  '\t' + 'open_water_parameter' +  '\t' + 'norm_open_water_parameter' + '\t' + 'sea_ice_parameter'  + '\t' + 'norm_sea_ice_parameter' + '\t' + 'snow_cover_parameter' + '\t' + 'norm_snow_cover_parameter' + '\n' )



for sim_date in args.date_time:
	print '****', sim_date, '****'
	months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names
	base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
	minute_of_day   = sim_date.hour*60 + sim_date.minute
	output_path     = os.path.join(base_path,'ship-' + str(sim_date.day).zfill(2) + months[sim_date.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
	p_header        = os.path.join(output_path ,'header_d01.nc')
	p_data          = glob.glob(output_path+'summedPES*.h5')[0]
	sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
	
	p_header    = os.path.join(output_path ,'header_d01.nc')
	p_data 		= glob.glob(output_path+'summedPES*.h5')[0]
	bare_land 	= glob.glob(output_path+'gridded_fraction_bare_land*.pckl')[0]
	open_ocean 	= glob.glob(output_path+'gridded_fraction_open_ocean*.pckl')[0]
	sea_ice 	= glob.glob(output_path+'gridded_fraction_sea_ice*.pckl')[0]
	snow_cover 	= glob.glob(output_path+'gridded_fraction_snow_cover*.pckl')[0]
	tundra_er 	= glob.glob(output_path+'gridded_fraction_tundra*.pckl')[0]

	Conc_var = PES.get_var(p_data, 'Conc_pCol300') 

	bare_land_grid 	= openLandParameters(bare_land)
	open_ocean_grid = openLandParameters(open_ocean)
	sea_ice_grid 	= openLandParameters(sea_ice)
	snow_cover_grid = openLandParameters(snow_cover)
	tundra_er_grid  = openLandParameters(tundra_er)

	landcovers = [
		['Bare Land',bare_land_grid  ,plt.cm.Oranges],
		['mixed Tundra, erodibility>0.5',tundra_er_grid,plt.cm.Reds],
		['Open Ocean',open_ocean_grid,plt.cm.Blues],
		['Sea Ice',sea_ice_grid 	 ,plt.cm.Greens],
		['Snow Cover',snow_cover_grid,plt.cm.Purples],
	]

	#define the figure
	fig, axes = plt.subplots(3,2,figsize=(14, 14), facecolor='w', edgecolor='k')
	fig.tight_layout()
	i = 0 
	p_line = [sim_start_datetime.strftime("%Y%m%d-%H%M")]
	for ax in axes.flat[:5]:
		ax.set_title(landcovers[i][0])
		print landcovers[i][0]
		ml = makeMap(ax)

		#re-project the FLEXPART grid
		xlat = PES.get_var(p_header, 'XLAT')
		xlon = PES.get_var(p_header, 'XLONG')
		x,y=ml(xlon,xlat)

		land_cover_grid = landcovers[i][1]
		#for tundra, ignore any portions covered in snow 
		if landcovers[i][0] == 'mixed Tundra, erodibility>0.5':
			land_cover_grid = landcovers[i][1] - landcovers[4][1]
			land_cover_grid[land_cover_grid < 0] = 0

		PES_f_landcover =  Conc_var*land_cover_grid
		landcover_parameter = np.nansum(PES_f_landcover)
		norm_landcover_parameter = landcover_parameter/np.nansum(Conc_var)
		max_val  = np.nanmax(PES_f_landcover)
		print landcover_parameter, norm_landcover_parameter,np.nansum(Conc_var),np.nansum(landcovers[i][1])
		#print max_val

		#make the contour plots
		levels = np.arange(0,max_val,max_val/2000)
		lvTmp = np.linspace(0.2,1.0,len(levels)-1)
		cmTmp = landcovers[i][2](lvTmp)
		newCmap = mcol.ListedColormap(cmTmp)
		
		newCmap.set_under(color='w')

		cl = ml.contourf(x,y,PES_f_landcover, levels = levels, cmap=newCmap,zorder = 1,vmin=max_val/2000, alpha = 1) 
		p_line.append(round(landcover_parameter,2))
		p_line.append(round(norm_landcover_parameter,3))

		i+=1

	#write to file
	if args.save_params == True:
		with open(p_file,'a') as pf:
			line = '\t'.join(str(x) for x in p_line)
			pf.write(line + '\n')

	#plt.savefig(os.path.join(output_path , 'surface_cover_source_contributions_'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png'), bbox_inches='tight', dpi=300)
	#plt.show()
	plt.close(fig)
	#20140714-1251 20140715-1733 20140716-2152 20140717-1929 20140718-2037 20140719-1618 20140721-1421 20140723-1441 20140724-2148 20140725-1950 20140726-1713 20140727-1747 20140728-2208 20140729-1340 20140730-1959 20140731-1715 20140801-1644 20140802-2003 20140803-1241 20140804-1457 20140805-2247 20140807-1250 20140808-1422 20140809-1410 20140810-1627 20140811-1407 20140812-1411

