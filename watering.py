import sqlite3
import RPi.GPIO as GPIO
import time
from datetime import datetime
import json
current_date_and_time = datetime.now()
print("The current date and time is", current_date_and_time)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

moisture_data = 5

relay1a = 26
relay2a = 19
relay3a = 20
relay4a = 21
relay5a = 16
relay6a = 13
relay7a = 6
relay8a = 5
relay1b = 27
relay2b = 17

relayNO = GPIO.LOW
relayNC = GPIO.HIGH
   

GPIO.setup(relay1a, GPIO.OUT, initial=relayNO)   
GPIO.setup(relay2a, GPIO.OUT, initial=relayNO)  
GPIO.setup(relay3a, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay4a, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay5a, GPIO.OUT, initial=relayNO)   
GPIO.setup(relay6a, GPIO.OUT, initial=relayNO)   
GPIO.setup(relay7a, GPIO.OUT, initial=relayNO)  
GPIO.setup(relay8a, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay1b, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay2b, GPIO.OUT, initial=relayNO) 


relay1aSts = GPIO.input(relay1a)
relay2aSts = GPIO.input(relay2a)
relay3aSts = GPIO.input(relay3a)
relay4aSts = GPIO.input(relay4a)
relay5aSts = GPIO.input(relay5a)
relay6aSts = GPIO.input(relay6a)
relay7aSts = GPIO.input(relay7a)
relay8aSts = GPIO.input(relay8a)
relay1bSts = GPIO.input(relay1b)
relay2bSts = GPIO.input(relay2b)

print("zone1 is ", relay1aSts)
print("zone2 is ", relay2aSts)
print("zone3 is ", relay3aSts)
print("zone4 is ", relay4aSts)
print("zone5 is ", relay5aSts)
print("zone6 is ", relay6aSts)

def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_zonemoist(x):
		conn = get_db_connection()
		y = str(x)
		print('getting moisture for '+y)
		sql = 'SELECT moist_soil_'+y+' FROM weather where moist_soil_2 is not null order by ID DESC limit 1; '
		print(sql)
		moisture = conn.execute(sql).fetchone()
		if moisture is None:
			print('no rows')
			moisture_data = 10  
		else:
			print('got record')
			moisture_data = moisture[0]
			if moisture_data is None:
				print('no value')
				moisture_data = 10
			print(moisture_data)
		conn.close()
		return(moisture_data)

waterdays = [0,2,4,6] # Mon, Wed, Fri
todaynum = 0
todaynum = current_date_and_time.weekday()
if todaynum in waterdays:
		print('watering day')
		if 10 <= current_date_and_time.hour <= 15: # water between 9am and 3pm
			print('watering hours')
			zones = ["1","2","3","4"]
			print("turning on pump")
			for z in zones:
				if z == 1:
					print('getting moisture for chaos')
					moisture_data = get_zonemoist((2))
				elif z == 2 or z == 3:
					print('getting moisture for S')
					moisture_data = get_zonemoist((3))	
				else:
					print('checking moisture for zone '+z)  # check kpa of beds to see if they are two wet
					moisture_data = get_zonemoist(4)
				print('moisture is: '+str(moisture_data))
				if moisture_data < 3:
					print('zone '+ z + ' is plenty moist')
				else:
					print('turning on zone '+ z +' for 25 min')
					current_date_and_time = datetime.now()
					print(current_date_and_time)
					GPIO.output(relay1b, GPIO.HIGH)
					GPIO.output(relay2b, GPIO.HIGH)
					GPIO.output(relay7a, GPIO.HIGH)
					GPIO.output(relay8a, GPIO.HIGH)
					if z == "1":
						GPIO.output(relay1b, GPIO.HIGH)
						GPIO.output(relay2b, GPIO.HIGH)
						GPIO.output(relay1a, GPIO.HIGH)
					if z == "2": 
						GPIO.output(relay1b, GPIO.HIGH)
						GPIO.output(relay2b, GPIO.HIGH)
						GPIO.output(relay2a, GPIO.HIGH)
					if z == "3":
						GPIO.output(relay1b, GPIO.HIGH)
						GPIO.output(relay2b, GPIO.HIGH)
						GPIO.output(relay3a, GPIO.HIGH)
					if z == "4" :
						GPIO.output(relay1b, GPIO.HIGH)
						GPIO.output(relay2b, GPIO.HIGH)
						GPIO.output(relay4a, GPIO.HIGH)
					conn = get_db_connection()
					conn.execute('INSERT INTO watering (zone) VALUES (?)', (z))
					conn.commit()
					time.sleep(1500)
					GPIO.output(relay1b, GPIO.LOW)
					GPIO.output(relay2b, GPIO.LOW)
					GPIO.output(relay7a, GPIO.LOW)
					GPIO.output(relay8a, GPIO.LOW)
					print('turning off zone '+ z)
					current_date_and_time = datetime.now()
					print(current_date_and_time)
					if z == "1":
						GPIO.output(relay1a, GPIO.LOW)
					if z == "2": 
						GPIO.output(relay2a, GPIO.LOW)
					if z == "3":
						GPIO.output(relay3a, GPIO.LOW)
					if z == "4" :
						GPIO.output(relay4a, GPIO.LOW)
					conn = get_db_connection()
					current_date_and_time = datetime.now()
					conn.execute('UPDATE watering SET end_time = ? WHERE zone = ? AND id in (select max(id) from watering where zone = ?)', (z, current_date_and_time,z))
					conn.commit()
					moisture_data = get_zonemoist(z)
					print('moisture after watering:'+ str(moisture_data))
					current_date_and_time = datetime.now()
					print(current_date_and_time)
		else:
			GPIO.output(relay7a, GPIO.LOW)
			GPIO.output(relay8a, GPIO.LOW)
			GPIO.output(relay1b, GPIO.LOW)
			GPIO.output(relay2b, GPIO.LOW)					
print('exiting')			
exit()			
