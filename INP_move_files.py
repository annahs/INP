#!/usr/bin/env python
# -- coding: UTF-8 --
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import os
import numpy as np                         
import dateutil
import argparse
import glob
from pprint import pprint
from datetime import datetime   
from shutil import copyfile
import FLEXPART_PES_NETCARE_module as PES




parser = argparse.ArgumentParser(description='''
    calculates overlaps of PES cells in FLEXPART output with shapefiles for sea ice, land, and snow cover
  ''')
parser.add_argument('date_time',  help ='date(s) and time(s) of interest',nargs='+',type=PES.valid_date)
args = parser.parse_args()



for sim_date in args.date_time:
	print '****', sim_date, '****'
	months = {7:'July',8:'Aug'}         #needed due to non-standard month formatting in file names
	base_path = '/Users/mcallister/projects/INP/FLEXPART-WRF/'
	minute_of_day   = sim_date.hour*60 + sim_date.minute
	output_path     = os.path.join(base_path,'ship-' + str(sim_date.day).zfill(2) + months[sim_date.month] + '-backward','output_' + str(1+PES.roundValue(minute_of_day, 20)).zfill(5) + '/')
	input_path 		= '/Users/mcallister/projects/INP/FLEXPART-WRF/surface_cover_PES_analysis/'
	p_header        = os.path.join(output_path ,'header_d01.nc')
	sim_start_datetime = dateutil.parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))


	landcover_plot = glob.glob(output_path+'snow_ice_cover_*.png')[0]
	landcover_source = glob.glob(output_path+'surface_cover_source_contributions_*.png')[0]

	landcover_plot_new_locn = os.path.join(input_path, 'snow_ice_cover_'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png' )
	landcover_source_new_locn = os.path.join(input_path, 'surface_cover_source_contributions_'+sim_start_datetime.strftime("%Y%m%d-%H%M") + '_AmundsenINP.png')


	copyfile(landcover_plot, landcover_plot_new_locn)
	copyfile(landcover_source, landcover_source_new_locn)

