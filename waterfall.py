#################
### waterfall ###
#################


import logging
import configparser
import os
import sys
from renogybt import BatteryClient, DataLogger, Utils
import RPi.GPIO as GPIO
import time
from datetime import datetime
import json
import sqlite3
logging.basicConfig(level=logging.DEBUG)

current = 0.0
voltage = 0.0


 


def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_raddata():
		conn = get_db_connection()
		sql = 'SELECT solar_rad FROM weather  order by ID DESC limit 1; '
		solarrad = conn.execute(sql).fetchone()
		if solarrad is None:
			#print('no rows')
			solarrad_data = 0  
		else:
			solarrad_data = solarrad[0]
			if solarrad_data is None:
				solarrad_data = 0
		conn.close()
		return(solarrad_data)

def get_battdata():
	conn = get_db_connection()
	battdata = conn.execute('SELECT batt_current, batt_voltage, batt_rem_charge, batt_capacity from battdata order by ID DESC limit 1; ').fetchone()
	#print(battdata)
	batt_current = battdata['batt_current']
	batt_voltage = battdata['batt_voltage']
	batt_rem_charge = battdata['batt_rem_charge']
	batt_capacity = battdata['batt_capacity']
	conn.close()
	if battdata is None:
		abort(404)
	return ([batt_current, batt_voltage, batt_rem_charge, batt_capacity])



current_date_and_time = datetime.now()
print("The current date and time is", current_date_and_time)
raddata = get_raddata()
print("Solar radiation is: "+str(raddata))
batt_data = get_battdata()
bcurrent = batt_data[0]
bvoltage = batt_data[1]
brc = batt_data[2]
bcap = batt_data[3]
print("battery voltage: "+str(bvoltage))
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

relay4b = 23


relayNO = GPIO.LOW
relayNC = GPIO.HIGH
   
GPIO.setup(relay4b, GPIO.OUT, initial=relayNO) 



relay4bSts = GPIO.input(relay4b)


print("Waterfall is ", relay4bSts)

if raddata > 100 and  8 <= current_date_and_time.hour <= 17 and bvoltage >=12: # water between 9am and 3pm
	GPIO.output(relay4b, GPIO.HIGH)
	print('waterfall on')	
else:
	GPIO.output(relay4b, GPIO.LOW)
	print('waterfall off')
#time.sleep(3500)
sys.exit()
