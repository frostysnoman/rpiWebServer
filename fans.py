#################
### FANS ########
#################

import os
import sys
import sqlite3
import RPi.GPIO as GPIO
import time
from datetime import datetime
import json

				

def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_raddata():
		conn = get_db_connection()
		sql = 'SELECT solar_rad FROM weather where id IN (select max(ID) from weather) '
		#print(sql)
		solarrad = conn.execute(sql).fetchone()
		#print(solarrad)
		solarrad_data = solarrad[0]
		if solarrad is None:
			print('no rows')
			solarrad_data = 0  
		else:
			solarrad_data = solarrad[0]
			if solarrad_data is None:
				solarrad_data = 0
		conn.close()
		return(solarrad_data)

def get_battdata():
	conn = get_db_connection()
	battdata = conn.execute('SELECT batt_current, batt_voltage, batt_rem_charge, batt_capacity from battdata where ID in (select max(ID) from battdata) ').fetchone()
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

relay1b = 27
relay2b = 17
relay3b = 18
relay4b = 23
relay5b = 24
relay6b = 4
relay7b = 3
relay8b = 2
fan1 = 14
fan2 = 12
relayNO = GPIO.LOW
relayNC = GPIO.HIGH

GPIO.setup(relay5b, GPIO.OUT, initial=relayNO)
GPIO.setup(relay6b, GPIO.OUT, initial=relayNO)
GPIO.setup(relay7b, GPIO.OUT, initial=relayNO)
GPIO.setup(relay8b, GPIO.OUT, initial=relayNO)
GPIO.setup(fan1, GPIO.OUT, initial=relayNO)
GPIO.setup(fan2, GPIO.OUT, initial=relayNO)

relay5bSts = GPIO.input(relay5b)
relay6bSts = GPIO.input(relay6b)
relay7bSts = GPIO.input(relay7b)
relay8bSts = GPIO.input(relay8b)
fan1Sts = GPIO.input(fan1)
fan2Sts = GPIO.input(fan2)
print("East Underground Fan is ", relay8bSts)
print("West Underground Fan is ", relay7bSts)
print("South Turbulator is ", relay6bSts)
print("North Turbulator is ", relay5bSts)
print("cpuFan1 is ",fan1Sts)
print("cpuFan2 is ",fan2Sts)
GPIO.output(fan1, GPIO.HIGH)
GPIO.output(fan2, GPIO.HIGH)

if raddata > 300 and  8 <= current_date_and_time.hour <= 17 and bvoltage > 13: # water between 9am and 3pm
	GPIO.output(relay7b, GPIO.HIGH)
	GPIO.output(relay6b, GPIO.HIGH)
	GPIO.output(relay5b, GPIO.HIGH)
	GPIO.output(relay8b, GPIO.HIGH)
	print('turning fans on')
	relay5bSts = GPIO.input(relay5b)
	relay6bSts = GPIO.input(relay6b)
	relay7bSts = GPIO.input(relay7b)
	relay8bSts = GPIO.input(relay8b)

	print("East Underground Fan is ", relay8bSts)
	print("West Underground Fan is ", relay7bSts)
	print("South Turbulator is ", relay6bSts)
	print("North Turbulator is ", relay5bSts)
else:
	GPIO.output(relay7b, GPIO.LOW)
	GPIO.output(relay6b, GPIO.LOW)
	GPIO.output(relay5b, GPIO.LOW)
	GPIO.output(relay8b, GPIO.LOW)
	print('turning fans off')
	relay5bSts = GPIO.input(relay5b)
	relay6bSts = GPIO.input(relay6b)
	relay7bSts = GPIO.input(relay7b)
	relay8bSts = GPIO.input(relay8b)

	print("East Underground Fan is ", relay8bSts)
	print("West Underground Fan is ", relay7bSts)
	print("South Turbulator is ", relay6bSts)
	print("North Turbulator is ", relay5bSts)	

print('out of loop')
relay5bSts = GPIO.input(relay5b)
relay6bSts = GPIO.input(relay6b)
relay7bSts = GPIO.input(relay7b)
relay8bSts = GPIO.input(relay8b)
fan1Sts = GPIO.input(fan1)
fan2Sts = GPIO.input(fan2)
print("East Underground Fan is ", relay8bSts)
print("West Underground Fan is ", relay7bSts)
print("South Turbulator is ", relay6bSts)
print("North Turbulator is ", relay5bSts)
print("CPU Fan1 is ", fan1Sts)
print("CPU Fan2 is ", fan2Sts)

#time.sleep(3500)
sys.exit()
