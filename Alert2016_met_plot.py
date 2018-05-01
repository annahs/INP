#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import matplotlib.pyplot as plt
import numpy as np
import os
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import matplotlib.colors
from dateutil import parser
from matplotlib import dates
import math
import pandas as pd


daily_precip_file = '/Users/mcallister/projects/INP/Alert_INP2016/docs/eng-daily-01012016-12312016.txt'
hourly_met_file   = '/Users/mcallister/projects/INP/Alert_INP2016/docs/eng-hourly-03012016-03312016.txt'
INP_file		  = '/Users/mcallister/projects/INP/Alert_INP2016/bin/SSI INP concentrations.txt'

INPs = []
with open(INP_file, 'r') as f:
	f.readline()
	
	for line in f:
		newline 	= line.split('\t')
		mid_time	= parser.parse(newline[0] + '-' + newline[4], dayfirst=False)
		INP15		= newline[5] # number/L
		INP15negerr = newline[6]
		INP15poserr = newline[7]
		INP20		= newline[8]
		INP20negerr = newline[9]
		INP20poserr = newline[10]
		INP25		= newline[11]
		INP25negerr = newline[12]
		INP25poserr = newline[13]
		INPs.append([mid_time,INP15,INP15negerr,INP15poserr,INP20,INP20negerr,INP20poserr,INP25,INP25negerr,INP25poserr])



precips = []
with open(daily_precip_file, 'r') as f:
	for line in range(0,26):
		f.readline()
	
	for line in f:
		newline 			= line.split('\t')
		precip_date = datetime(int(newline[1]),int(newline[2]),int(newline[3]))

		if datetime(2016,3,10) <= precip_date < datetime(2016,3,31):
			rain = float(newline[15])  #mm
			snow = float(newline[17])
			total = float(newline[19])
			precips.append([precip_date, rain,snow,total])

met_data = []
with open(hourly_met_file, 'r') as f:
	for line in range(0,17):
		f.readline()
	
	for line in f:
		newline = line.split('\t')
		met_datetime_LST = parser.parse(newline[0])
		met_datetime_UTC = met_datetime_LST + timedelta(hours=4)
		

		if datetime(2016,3,10) <= met_datetime_UTC < datetime(2016,3,31):
			temp = float(newline[6]) #deg C
			RH = float(newline[10]) #%
			try:
				wind_dir = float(newline[12]) #10s degreses
			except:
				wind_dir = np.nan
			wind_spd = float(newline[14]) #km/h
			met_data.append([met_datetime_UTC,temp,RH,wind_spd,wind_dir*10])


#plots
fig = plt.figure(figsize = (10,14))

hfmt = dates.DateFormatter('%d')

ax0=  plt.subplot2grid((6,1), (0,0), colspan=1,rowspan = 1)
ax1=  plt.subplot2grid((6,1), (1,0), colspan=1,rowspan = 1)
ax2=  plt.subplot2grid((6,1), (2,0), colspan=1,rowspan = 1)
ax3=  plt.subplot2grid((6,1), (3,0), colspan=1,rowspan = 1)
ax4 = plt.subplot2grid((6,1), (4,0), colspan=1,rowspan = 1)
ax5 = plt.subplot2grid((6,1), (5,0), colspan=1,rowspan = 1)

INP_date 	= [dates.date2num(row[0]) for row in INPs]
INP15		= [float(row[1]) for row in INPs]
INP15negerr = [float(row[2]) for row in INPs]
INP15poserr = [float(row[3]) for row in INPs]
INP20		= [float(row[4]) for row in INPs]
INP20negerr = [float(row[5]) for row in INPs]
INP20poserr = [float(row[6]) for row in INPs]
INP25		= [float(row[7]) for row in INPs]
INP25negerr = [float(row[8]) for row in INPs]
INP25poserr = [float(row[9]) for row in INPs]

ax0.errorbar(INP_date,INP15,yerr=[INP15negerr, INP15poserr],color = 'k', marker='s',label='-15$^\circ$C')
ax0.errorbar(INP_date,INP20,yerr=[INP20negerr, INP20poserr],color = 'r', marker='o',label='-20$^\circ$C')
ax0.errorbar(INP_date,INP25,yerr=[INP25negerr, INP25poserr],color = 'b', marker='^',label='-25$^\circ$C')
ax0.xaxis.set_major_formatter(hfmt)
ax0.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax0.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax0.tick_params(labelbottom='off')    
ax0.set_ylabel('INP/L')
ax0.set_yscale('log')
ax0.set_ylim(1e-3,1)
ax0.legend(loc='upper left',numpoints =1,borderpad=0.1,fontsize=10)
ax0.grid(b=True)

precips_date = [dates.date2num(row[0]) for row in precips]
precips_rain = [row[1] for row in precips]
precips_snow = [row[2] for row in precips]
precips_tot  = [row[3] for row in precips]

ax1.bar(precips_date,precips_tot, width = 1)
ax1.xaxis.set_major_formatter(hfmt)
ax1.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax1.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax1.tick_params(labelbottom='off')    
ax1.set_ylabel('Total Precip (mm)')
ax1.grid(b=True)

met_date = [dates.date2num(row[0]) for row in met_data]
met_temp = [row[1] for row in met_data]
met_RH   = [row[2] for row in met_data]
met_wind_spd  = [row[3] for row in met_data]
met_wind_dir  = [row[4] for row in met_data]

ax2.plot(met_date,met_temp, '-ro')
ax2.xaxis.set_major_formatter(hfmt)
ax2.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax2.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax2.tick_params(labelbottom='off')    
ax2.set_ylabel('Temperature (C)')
ax2.grid(b=True)

ax3.plot(met_date,met_RH, '-bo')
ax3.xaxis.set_major_formatter(hfmt)
ax3.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax3.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax3.tick_params(labelbottom='off')    
ax3.set_ylabel('RH (%)')
ax3.grid(b=True)

ax4.plot(met_date,met_wind_spd, '-go')
ax4.xaxis.set_major_formatter(hfmt)
ax4.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax4.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax4.tick_params(labelbottom='off')    
ax4.set_ylabel('Wind Speed (km/h)')
ax4.grid(b=True)

ax5.plot(met_date,met_wind_dir, '-ko')
ax5.xaxis.set_major_formatter(hfmt)
ax5.set_xlim(dates.date2num(datetime(2016,3,10)), dates.date2num(datetime(2016,3,31)))
ax5.set_ylim(0,360)
ax5.xaxis.set_major_locator(dates.DayLocator(interval = 1))
ax5.set_ylabel('Wind Direction (deg)')
ax5.set_xlabel('March 2016')
ax5.grid(b=True)

plt.subplots_adjust(hspace=0.1)
plt.subplots_adjust(wspace=0.00)

plt.savefig('/Users/mcallister/projects/INP/Alert_INP2016/bin/Alert_20130310-20130330_met_data_withINP.png',bbox_inches='tight')


plt.show()

