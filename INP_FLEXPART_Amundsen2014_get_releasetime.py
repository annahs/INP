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
from  dateutil import parser
import argparse
import glob
from pprint import pprint
from datetime import datetime





base_path = '/Volumes/storage/FLEXPART/Amundsen_2014/FLEXPART-WRF/ship-22July-backward/'

for dirName, subdirList, fileList in os.walk(base_path):
    print('Found directory: %s' % dirName)
    for sname in subdirList:
        if sname.startswith('output_'):
            print sname
            minute = int(sname[7:])
            #print minute/60, minute%60
            print datetime(2014,7,22,minute/60,(minute%60)+1)
            p_header = os.path.join(base_path,sname,'header_d01.nc')
            #sim_start_datetime = parser.parse(str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_DATE')) + str(PES.getHeaderAttribute(p_header, 'SIMULATION_START_TIME')))
            #print sim_start_datetime

            f_head = h5py.File(p_header, mode='r')
            f_head_attr = f_head.attrs.items()
            for item in f_head_attr:
                key = item[0]
                value = item[1][0]
                if key == 'SIMULATION_START_TIME':
                    print  parser.parse('2014-7-22 ' + str(value).zfill(6))
                    print '\n'
    sys.exit()

