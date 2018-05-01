#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import os
import numpy as np    
from pprint import pprint
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import dates
import math
import calendar
import Alert_sampling_times as AL
from mysql_db_connection import dbConnection
from dateutil import parser

sample_times = AL.getHours('INP25','all')

#create db connection and cursor
database_connection = dbConnection('CABM_SP2')
cnx = database_connection.db_connection
cursor = database_connection.db_cur

timeseries_data = []

for sample in sample_times:
	start_analysis				= parser.parse(sample[0])
	end_analysis				= parser.parse(sample[1])
	UNIX_start_analysis			= calendar.timegm(start_analysis.utctimetuple())
	UNIX_end_analysis			= calendar.timegm(end_analysis.utctimetuple())
	instr_location_ID	 		= 1
	instr_ID					= 3

	sample_data = []

	cursor.execute(('''SELECT 
			UNIX_UTC_ts_int_start,
			UNIX_UTC_ts_int_end,	
			total_interval_mass,
			total_interval_mass_uncertainty,
			total_interval_number,
			total_interval_volume,
			fraction_of_mass_sampled,
			fraction_of_mass_sampled_uncertainty
		FROM sp2_time_intervals_locn'''+ str(instr_location_ID)+'''  
		WHERE UNIX_UTC_ts_int_start >= %s 
			and UNIX_UTC_ts_int_start < %s
			and instr_ID = %s'''),
		(UNIX_start_analysis,UNIX_end_analysis,instr_ID))	
		

	data = cursor.fetchall()
	for row in data:
		interval_start 				= row[0]
		interval_end 				= row[1]
		interval_mid 				= interval_start + (interval_end-interval_start)/2
		fraction_of_mass_sampled 	= np.float32(row[6])
		fraction_of_mass_sampled_err= np.float32(row[7])
		mass_conc 					= np.float32(row[2])/(np.float32(row[5])*fraction_of_mass_sampled)
		mass_conc_err 				= np.float32(row[3])/(np.float32(row[5])*fraction_of_mass_sampled)
		numb_conc 					= np.float32(row[4])/(np.float32(row[5]))

		sample_data.append([mass_conc,mass_conc_err])

	time 			= start_analysis + (end_analysis-start_analysis)/2
	mass_conc	 	= np.mean([row[0] for row in sample_data])
	mass_conc_err 	= np.mean([row[1] for row in sample_data])
	timeseries_data.append([start_analysis,end_analysis,mass_conc,mass_conc_err])

#write to file
file = '/Users/mcallister/projects/INP/Alert_INP2016/docs/Alert2016_rBC_mass_concentrations_for_INP_sample_times.txt'
with open(file,'w') as pf:
	pf.write('sample_start_date\tsample_start_time\tsample_end_date\tsample_end_time\trBC_mass_conc(ng/m3)\trBC_mass_conc_uncertainty\n')
	for line in timeseries_data:
		newline = '\t'.join(str(x) for x in line)
		pf.write(newline + '\n')


#plotting
times 			= [row[0] for row in timeseries_data]
mass_concs	 	= [row[2] for row in timeseries_data]
mass_concs_err  = [row[3] for row in timeseries_data]

hfmt = dates.DateFormatter('%Y%m%d %H:%M')
fig = plt.figure(figsize=(12,10))

ax1 = plt.subplot2grid((1,1), (0,0))

ax1.errorbar(times,mass_concs, yerr = mass_concs_err, color = 'b', marker = 'o')
ax1.xaxis.set_major_formatter(hfmt)
ax1.set_ylabel('rBC mass concentration (ng/m3)')
ax1.set_xlabel('Time')
ymin, ymax = ax1.get_ylim()
ax1.set_ylim(0,ymax)


#fig.suptitle(title, fontsize=14)

plt.show()


