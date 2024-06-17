'''
	Greenhouse Automation script
'''
import logging
from logging.config import dictConfig
import sqlite3
import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, request, jsonify, request, url_for, flash, redirect, session
from gpiozero import CPUTemperature
import uuid
import os
import json
import subprocess
import string
from datetime import datetime
current_date_and_time = datetime.now()

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",	
                "formatter": "default",
            },
        	  "file": {
                "class": "logging.FileHandler",
                "filename": "flask.log",
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["file"]}
#        "root": {"level": "DEBUG", "handlers": ["console"]},
    }
)


app = Flask(__name__)
 
  
app.config['SECRET_KEY'] = '12345'

valvestemp_data = 0.0
headtemp_data = 0.0
pdepth = 0.0
cdepth = 0.0
ms1 = 100
ms2 = 100
ms3 = 100
ms4 = 100
kasarun = ''

cstat = '?'
pohstat = '?'
pihstat = '?'
apstat = '?'
efstat = '?'
tbdstat = '?'



def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn
	
def get_vtemps():
	conn = get_db_connection()
	valvestemp = conn.execute('SELECT temp FROM temps where loc = "Valves" order by ID DESC limit 1; ').fetchone()
	valvestemp_data = valvestemp['temp']
	print(valvestemp_data)
	conn.close()
	if valvestemp is None:
		abort(404)
	return valvestemp_data
	
	
def get_pdepths():
	conn = get_db_connection()
	pdepth_data = 0.0
	depth = conn.execute('SELECT depth FROM depths where loc = "pond" order by ID DESC limit 1; ').fetchone()
	if depth is None:
		pdepth_data = '0'
	else: 
		pdepth_data = depth['depth']
	print(pdepth_data)
	conn.close()
	return pdepth_data	
	
def get_cdepths():
	conn = get_db_connection()
	cdepth_data = 0.0
	cdepth = conn.execute('SELECT depth FROM depths where loc = "cistern" order by ID DESC limit 1; ').fetchone()
	if cdepth is None:
		cdepth_data = '0'
	else: 
		cdepth_data = cdepth['depth']
	print(cdepth_data)
	conn.close()
	return cdepth_data	
	
	
def get_zonemoist():
		conn = get_db_connection()
		sql = 'SELECT moist_soil_1, moist_soil_2, moist_soil_3, moist_soil_4 FROM weather where moist_soil_2 is not null order by ID DESC limit 1; '
		moisture = conn.execute(sql).fetchone()
		ms1 = moisture['moist_soil_1']
		ms2 = moisture['moist_soil_2']
		ms3 = moisture['moist_soil_3']
		ms4 = moisture['moist_soil_4']
		print(ms1)
		conn.close()
		return(moisture)
	
def get_htemps():
	conn = get_db_connection()
	headtemp = conn.execute('SELECT temp FROM temps where loc = "Head" order by ID DESC limit 1; ').fetchone()
	headtemp_data = headtemp['temp']
	print(headtemp_data)
	conn.close()
	if headtemp is None:
		abort(404)
	return headtemp_data

def get_120():
	kasastaterun = "kasa --host 192.168.150.211 state"
	print('get120')
	ko = subprocess.run(kasastaterun.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,)
	lines = ko.stdout.splitlines()
	c = lines[6]
	c2 = str(c, encoding='utf-8')
	print(c2)
	cstat = c2[27:28]
	poh = lines[7]
	print(poh)
	poh2 = str(poh, encoding='utf-8')
	pohstat = poh2[30:31]
	pih = lines[8]
	pih2 = str(pih, encoding='utf-8')
	pihstat = pih2[30:31]
	ap = lines[9]
	ap2 = str(ap, encoding='utf-8')
	apstat = ap2[28:29]
	ef = lines[10]
	ef2 = str(ef, encoding='utf-8')
	efstat = ef2[26:28]
	tbd = lines[11]
	tbd2 = str(tbd, encoding='utf-8')
	tbdstat = tbd2[29:30]
		
	return([cstat, pohstat, pihstat, apstat, efstat, tbdstat])

def log_120(plug):
	print(plug)
	conn = get_db_connection()
	conn.execute('INSERT INTO powerstats (PLUG) VALUES (?)', (plug,))
	conn.commit()

def update_120(plug):
	print(plug)
	current_date_and_time = datetime.now()
	conn = get_db_connection()
	conn.execute('UPDATE powerstats SET end_time = ? where id in (select max(id) from powerstate where plug = ?)', (current_date_and_time, plug))
	conn.commit()	
	
 
cputemp = CPUTemperature().temperature
valvestemp_data = get_vtemps()
headtemp_data = get_htemps()
moisture = get_zonemoist()
pdepth = get_pdepths()
cdepth = get_cdepths()
hvlist = get_120()
cstat = hvlist[0]
pohstat = hvlist[1]
pihstat = hvlist[2]
apstat = hvlist[3]
efstat = hvlist[4]
tbdstat = hvlist[5]

ms1 = moisture['moist_soil_1']
ms2 = moisture['moist_soil_2']
ms3 = moisture['moist_soil_3']
ms4 = moisture['moist_soil_4']


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
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
relay3b = 18
relay4b = 23
relay5b = 24
relay6b = 4
relay7b = 3
relay8b = 2

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
GPIO.setup(relay3b, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay4b, GPIO.OUT, initial=relayNO) 
GPIO.setup(relay5b, GPIO.OUT, initial=relayNO)   
GPIO.setup(relay6b, GPIO.OUT, initial=relayNO)   
GPIO.setup(relay7b, GPIO.OUT, initial=relayNO)  
GPIO.setup(relay8b, GPIO.OUT, initial=relayNO)


#https://towardsdatascience.com/python-webserver-with-flask-and-raspberry-pi-398423cc6f5d
	

    
    
    
@app.route("/")
def index():
	templateData = {
      'title' : 'GPIO Relay Status!',
      'cputemp'  : cputemp,
      'valvestemp_data' : valvestemp_data,
      'headtemp_data' : headtemp_data,
      'moist_soil_1' : ms1,
			'moist_soil_2' : ms2,
			'moist_soil_3' : ms3,
			'moist_soil_4' : ms4,
      }
	return render_template('home.html', **templateData)


@app.route("/air")
def air():
	relay4bSts = GPIO.input(relay4b)
	relay5bSts = GPIO.input(relay5b)
	relay6bSts = GPIO.input(relay6b)
	relay7bSts = GPIO.input(relay7b)
	relay8bSts = GPIO.input(relay8b)
	templateData = {
      'Relay4b'  : relay4bSts,
      'Relay5b'  : relay5bSts,
      'Relay6b'  : relay6bSts,
      'Relay7b'  : relay7bSts,
      'Relay8b'  : relay8bSts,
      }
	return render_template('air.html', **templateData)

@app.route("/water")
def water():
	relay1aSts = GPIO.input(relay1a)
	relay2aSts = GPIO.input(relay2a)
	relay3aSts = GPIO.input(relay3a)
	relay4aSts = GPIO.input(relay4a)
	templateData = {
      'Relay4b'  : relay1aSts,
      'Relay5b'  : relay2aSts,
      'Relay6b'  : relay3aSts,
      'Relay7b'  : relay4aSts,
      }
	return render_template('water.html', **templateData)
	
	@app.route("/power")
def power():
	hvlist = get_120()
	cstat = hvlist[0]
	pohstat = hvlist[1]
	pihstat = hvlist[2]
	apstat = hvlist[3]
	efstat = hvlist[4]
	tbdstat = hvlist[5]
	templateData = {
			'cstat' : cstat,
			'pohstat' : pohstat,
			'pihstat' : pihstat,
			'apstat' : apstat,
			'efstat' : efstat,
			'tbdstat' : tbdstat,
			'cdepth' :cdepth,
			'pdepth' : pdepth,
      }
	return render_template('water.html', **templateData)


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
	if deviceName == 'relay1a':
		actuator = relay1a
	if deviceName == 'relay2a':
		actuator = relay2a
	if deviceName == 'relay3a':
		actuator = relay3a
	if deviceName == 'relay4a':
		actuator = relay4a
	if deviceName == 'relay5a':
		actuator = relay5a
	if deviceName == 'relay6a':
		actuator = relay6a
	if deviceName == 'relay7a':
		actuator = relay7a
	if deviceName == 'relay8a':
		actuator = relay8a
	if deviceName == 'relay1b':
		actuator = relay1b
	if deviceName == 'relay2b':
		actuator = relay2b
	if deviceName == 'relay3b':
		actuator = relay3b
	if deviceName == 'relay4b':
		actuator = relay4b
	if deviceName == 'relay5b':
		actuator = relay5b
	if deviceName == 'relay6b':
		actuator = relay6b
	if deviceName == 'relay7b':
		actuator = relay7b
	if deviceName == 'relay8b':
		actuator = relay8b		
	if deviceName == 'testlight':
			actuator = 'testlight'
	if deviceName == 'pipeheater':
			actuator = 'pipeheater'	
	if deviceName == 'pondheater':
			actuator = 'pondheater'				
	if deviceName == 'eastfan':
			actuator = 'eastfan'				
	if deviceName == 'charger':
			actuator = 'charger'				
	if deviceName == 'aquapump':
			actuator = 'aquapump'	
	if action == "on":
		GPIO.output(actuator, GPIO.HIGH)
	if action == "off":
		GPIO.output(actuator, GPIO.LOW)
	if action =="turnon":
		#print('test')
		kasarun = "kasa --host 192.168.150.211 on --name "+actuator
		subprocess.run(kasarun.split())
		hvlist = get_120()
		cstat = hvlist[0]
		pohstat = hvlist[1]
		pihstat = hvlist[2]
		apstat = hvlist[3]
		efstat = hvlist[4]
		tbdstat = hvlist[5]
		log_120(actuator)
		
		
		
	if action =="turnoff":
		kasarun = "kasa --host 192.168.150.211 off --name "+actuator
		subprocess.run(kasarun.split())
		hvlist = get_120()
		cstat = hvlist[0]
		pohstat = hvlist[1]
		pihstat = hvlist[2]
		apstat = hvlist[3]
		efstat = hvlist[4]
		tbdstat = hvlist[5]
		log_120(actuator)
		
		     
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
	relay3bSts = GPIO.input(relay3b)
	relay4bSts = GPIO.input(relay4b)
	relay5bSts = GPIO.input(relay5b)
	relay6bSts = GPIO.input(relay6b)
	relay7bSts = GPIO.input(relay7b)
	relay8bSts = GPIO.input(relay8b)
   
	templateData = {
      'title' : 'GPIO Relay Status!',
      'Relay1a'  : relay1aSts,
      'Relay2a'  : relay2aSts,
      'Relay3a'  : relay3aSts,
      'Relay4a'  : relay4aSts,
      'Relay5a'  : relay5aSts,
      'Relay6a'  : relay6aSts,
      'Relay7a'  : relay7aSts,
      'Relay8a'  : relay8aSts,
      'Relay1b'  : relay1bSts,
      'Relay2b'  : relay2bSts,
      'Relay3b'  : relay3bSts,
      'Relay4b'  : relay4bSts,
      'Relay5b'  : relay5bSts,
      'Relay6b'  : relay6bSts,
      'Relay7b'  : relay7bSts,
      'Relay8b'  : relay8bSts,
      'cputemp'  : cputemp,
      'cdepth' :cdepth,
			'pdepth' : pdepth,
      'valvestemp_data': valvestemp_data,
      'headtemp_data' : headtemp_data,
      'moist_soil_1' : ms1,
			'moist_soil_2' : ms2,
			'moist_soil_3' : ms3,
			'moist_soil_4' : ms4,
			'cstat' : cstat,
			'pohstat' : pohstat,
			'pihstat' : pihstat,
			'apstat' : apstat,
			'efstat' : efstat,
			'tbdstat' : tbdstat,
      }
	return render_template('base.html', **templateData)
	

@app.route('/depth', methods=["POST"])
def add_ponddepth():
	pond_data = request.json
	print(pond_data)
	pond_value = pond_data.get('depth')
	pondloc_value = pond_data.get('loc')
	conn = get_db_connection()
	conn.execute('INSERT INTO depths (depth, loc) VALUES (?, ?)', (pond_value, pondloc_value))
	conn.commit()
	get_pdepths()
	get_cdepths()
	return "Success", 200, {"Access-Control-Allow-Origin": "*"}
    
@app.route('/temps', methods=["POST"])
def add_temp():
		temp_data = request.json
		print(temp_data)
		temp_value = temp_data.get('temp')
		temploc_value = temp_data.get('temploc')
		hum_value = temp_data.get('hum')
		conn = get_db_connection()
		conn.execute('INSERT INTO temps (temp, loc, hum) VALUES (?, ?, ?)', (temp_value, temploc_value, hum_value))
		conn.commit()
		get_vtemps()
			
		return "Success", 200, {"Access-Control-Allow-Origin": "*"}

if __name__ == "__main__":
#   app.run(host='192.168.1.50', port=443, debug=False, ssl_context=('cert.pem', 'key.pem'))
	#app.run(host='192.168.1.50', port=80, debug=True)
	app.run(host='192.168.150.100', port=80, debug=True)
