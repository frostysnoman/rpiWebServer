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
logging.basicConfig(filename='flask.log', level=logging.DEBUG)
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
pdts = current_date_and_time
cdepth = 0.0
cdts = current_date_and_time
ms1 = 100
ms2 = 100
ms3 = 100
ms4 = 100
ts1 = 0
ts2 = 0
ts3 = 0
tss4 = 0
kasarun = ''
bcurrent = 0.0
bvoltage = 0.0
brc = 0.0
bcap = 0.0
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
	pdts = current_date_and_time
	print(pdts)
	depth = conn.execute('SELECT depth, dts FROM depths where loc = "pond" order by dts DESC limit 1; ').fetchone()
	if depth is None:
		pdepth_data = '0'
	else: 
		pdepth_data = depth['depth']
		pdts = depth['dts']
	print(pdepth_data)
	print(pdts)
	conn.close()
	return pdepth_data, pdts
	
def get_cdepths():
	conn = get_db_connection()
	cdepth_data = 0.0
	cdts = current_date_and_time
	cdepth = conn.execute('SELECT depth, dts FROM depths where loc = "cistern" order by dts DESC limit 1; ').fetchone()
	if cdepth is None:
		cdepth_data = '0'
	else: 
		cdepth_data = cdepth['depth']
		cdts = cdepth['dts']
	print(cdepth_data)
	conn.close()
	return cdepth_data, cdts
	
	
def get_zonemoist():
		conn = get_db_connection()
		sql = 'SELECT moist_soil_1, moist_soil_2, moist_soil_3, moist_soil_4, temp_soil_1, temp_soil_2, temp_soil_3, temp_soil_4 FROM weather where moist_soil_2 is not null order by ID DESC limit 1; '
		moisture = conn.execute(sql).fetchone()
		ms1 = moisture['moist_soil_1']
		ms2 = moisture['moist_soil_2']
		ms3 = moisture['moist_soil_3']
		ms4 = moisture['moist_soil_4']
		ts1 = moisture['temp_soil_1']
		ts2 = moisture['temp_soil_2']
		ts3 = moisture['temp_soil_3']
		ts4 = moisture['temp_soil_4']
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

def get_battdata():
	conn = get_db_connection()
	battdata = conn.execute('SELECT batt_current, batt_voltage, batt_rem_charge, batt_capacity from battdata order by ID DESC limit 1; ').fetchone()
	print(battdata)
	batt_current = battdata['batt_current']
	batt_voltage = battdata['batt_voltage']
	batt_rem_charge = battdata['batt_rem_charge']
	batt_capacity = battdata['batt_capacity']
	conn.close()
	if battdata is None:
		abort(404)
	return ([batt_current, batt_voltage, batt_rem_charge, batt_capacity])


def get_120():
	kasastaterun = "kasa --host 192.168.150.211 state"
	print('get120')
	current_env = os.environ.copy()
	ko = subprocess.run(kasastaterun.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=current_env)
	print(ko)	
	lines = ko.stdout.splitlines()
	cstat = "?"
	pohstat = "?"
	pihstat = "?"
	apstat = "?"
	efstat = "?"
	tbdstat = "?"
	if len(lines) >= 31:
		c = lines[31]
		c2 = str(c, encoding='utf-8')
		cstat = c2[16:17]
		print("chargerstat: "+cstat)
	if len(lines) >= 48:
		poh = lines[48]
		poh2 = str(poh, encoding='utf-8')
		pohstat = poh2[16:17]
		print("pond heater stat: "+pohstat)
	if len(lines) >= 65:
		pih = lines[65]
		pih2 = str(pih, encoding='utf-8')
		pihstat = pih2[16:17]
		print("pipe heater stat: "+pihstat)
	if len(lines) >= 82:
		ap = lines[82]
		ap2 = str(ap, encoding='utf-8')
		apstat = ap2[16:17]
		print("aquaponic stat: "+apstat)
	if len(lines) >= 99:
		ef = lines[99]
		ef2 = str(ef, encoding='utf-8')
		efstat = ef2[16:17]
		print("east fan stat: "+efstat)
	if len(lines) >= 116:
		tbd = lines[116]
		tbd2 = str(tbd, encoding='utf-8')
		tbdstat = tbd2[16:17]
		print("tbdstat: "+tbdstat)
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
pdepth, pdts = get_pdepths()
cdepth, cdts = get_cdepths()
hvlist = get_120()
cstat = hvlist[0]
pohstat = hvlist[1]
pihstat = hvlist[2]
apstat = hvlist[3]
efstat = hvlist[4]
tbdstat = hvlist[5]

batt_data = get_battdata()
bcurrent = batt_data[0]
bvoltage = batt_data[1]
brc = batt_data[2]
bcap = batt_data[3]

ms1 = moisture['moist_soil_1']
ms2 = moisture['moist_soil_2']
ms3 = moisture['moist_soil_3']
ms4 = moisture['moist_soil_4']
ts1 = moisture['temp_soil_1']
ts2 = moisture['temp_soil_2']
ts3 = moisture['temp_soil_3']
ts4 = moisture['temp_soil_4']
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
	batt_data = get_battdata()
	bcurrent = batt_data[0]
	bvoltage = batt_data[1]
	brc = batt_data[2]
	bcap = batt_data[3]
	cputemp = CPUTemperature().temperature
	valvestemp_data = get_vtemps()
	headtemp_data = get_htemps()
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
      'ctf' : (cputemp *9/5) +32,
      'valvestemp_data' : valvestemp_data,
      'vtdf' : (valvestemp_data * 9/5) + 32,
      'headtemp_data' : headtemp_data,
      'htdf' : (headtemp_data *9/5) +32,
      'moist_soil_1' : ms1,
      'moist_soil_2' : ms2,
      'moist_soil_3' : ms3,
      'moist_soil_4' : ms4,
      'temp_soil_1' : ts1,
      'temp_soil_2' : ts2,
      'temp_soil_3' : ts3,
      'temp_soil_4' : ts4,	
      'cdepth' : cdepth,
      'cdts' : cdts,
      'pdepth' : pdepth,
      'pdts' : pdts,
      'batt_current' : bcurrent,
      'batt_voltage' : bvoltage,
      'batt_rem_chg' : brc,
      'batt_cap' : bcap,	
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
	relay4bSts = GPIO.input(relay4b)
	relay1bSts = GPIO.input(relay1b)
	relay2bSts = GPIO.input(relay2b)
	templateData = {
			'Relay1b'  : relay1bSts,
      'Relay2b'  : relay2bSts,
      'Relay1a'  : relay1aSts,
      'Relay2a'  : relay2aSts,
      'Relay3a'  : relay3aSts,
      'Relay4a'  : relay4aSts,
      'Relay4b'  : relay4bSts,
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
      }
	return render_template('power.html', **templateData)

@app.route("/refresh")
def refresh():
	cputemp = CPUTemperature().temperature
	valvestemp_data = get_vtemps()
	headtemp_data = get_htemps()
	moisture = get_zonemoist()
	pdepth, pdts = get_pdepths()
	cdepth, cdts = get_cdepths()
	hvlist = get_120()
	cstat = hvlist[0]
	pohstat = hvlist[1]
	pihstat = hvlist[2]
	apstat = hvlist[3]
	efstat = hvlist[4]
	tbdstat = hvlist[5]

	batt_data = get_battdata()
	bcurrent = batt_data[0]
	bvoltage = batt_data[1]
	brc = batt_data[2]
	bcap = batt_data[3]

	ms1 = moisture['moist_soil_1']
	ms2 = moisture['moist_soil_2']
	ms3 = moisture['moist_soil_3']
	ms4 = moisture['moist_soil_4']
	ts1 = moisture['temp_soil_1']
	ts2 = moisture['temp_soil_2']
	ts3 = moisture['temp_soil_3']
	ts4 = moisture['temp_soil_4']
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

	if valvestemp_data < 5:
		kasarun = "kasa --host 192.168.150.211 on --name testlight"
		subprocess.run(kasarun.split())
		time.sleep(10)
		kasarun = "kasa --host 192.168.150.211 on --name pipeheater"
		subprocess.run(kasarun.split())
		time.sleep(10)
	else: 
		kasarun = "kasa --host 192.168.150.211 off --name testlight"
		subprocess.run(kasarun.split())
		time.sleep(10)
		kasarun = "kasa --host 192.168.150.211 off --name pipeheater"
		subprocess.run(kasarun.split())
		time.sleep(10)
	if brc < 85:
		kasarun = "kasa --host 192.168.150.211 on --name charger"
		subprocess.run(kasarun.split())
	else:
		kasarun = "kasa --host 192.168.150.211 off --name charger"
		subprocess.run(kasarun.split())
	
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
      'ctf' : (cputemp *9/5) +32,
      'valvestemp_data' : valvestemp_data,
      'vtdf' : (valvestemp_data * 9/5) + 32,
      'headtemp_data' : headtemp_data,
      'htdf' : (headtemp_data *9/5) +32,
      'moist_soil_1' : ms1,
      'moist_soil_2' : ms2,
      'moist_soil_3' : ms3,
      'moist_soil_4' : ms4,
      'temp_soil_1' : ts1,
      'temp_soil_2' : ts2,
      'temp_soil_3' : ts3,
      'temp_soil_4' : ts4,	
      'cdepth' :cdepth,
      'cdts' : cdts,
      'pdepth' : pdepth,
      'pdst' : pdts,
      'batt_current' : bcurrent,
      'batt_voltage' : bvoltage,
      'batt_rem_chg' : brc,
      'batt_cap' : bcap,	
      }
      
	return render_template('home.html', **templateData)
	
@app.route("/mute")
def mute():
	GPIO.output(relay5b, GPIO.LOW)
	GPIO.output(relay6b, GPIO.LOW)		
	GPIO.output(relay7b, GPIO.LOW)		
	GPIO.output(relay8b, GPIO.LOW)		
	templateData = {
			'Relay4b'  : relay4bSts,
      'Relay5b'  : relay5bSts,
      'Relay6b'  : relay6bSts,
			'Relay8b'  : relay8bSts,
			'cstat' : cstat,
			'pohstat' : pohstat,
			'pihstat' : pihstat,
			'apstat' : apstat,
			'efstat' : efstat,
			'tbdstat' : tbdstat,
			'cputemp'  : cputemp,
      'ctf' : (cputemp *9/5) +32,
      'valvestemp_data' : valvestemp_data,
      'vtdf' : (valvestemp_data * 9/5) + 32,
      'headtemp_data' : headtemp_data,
      'htdf' : (headtemp_data *9/5) +32,
      'moist_soil_1' : ms1,
      'moist_soil_2' : ms2,
      'moist_soil_3' : ms3,
      'moist_soil_4' : ms4,
      'cdepth' :cdepth,
      'cdts' : cdts,
      'pdepth' : pdepth,
      'pdts' : pdts,
      }
	return render_template('base.html', **templateData)

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
		
	hvlist = get_120()
	cstat = hvlist[0]
	pohstat = hvlist[1]
	pihstat = hvlist[2]
	apstat = hvlist[3]
	efstat = hvlist[4]
	tbdstat = hvlist[5]
		     
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
      'cdepth' :cdepth,
			'pdepth' : pdepth,
      'cputemp'  : cputemp,
      'ctf' : (cputemp *9/5) +32,
      'valvestemp_data' : valvestemp_data,
      'vtdf' : (valvestemp_data * 9/5) + 32,
      'headtemp_data' : headtemp_data,
      'htdf' : (headtemp_data *9/5) +32,
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
	return render_template('home.html', **templateData)
	
@app.route("/PUMPON")
def pumpon():
	GPIO.output(relay1b, GPIO.HIGH)
	GPIO.output(relay2b, GPIO.HIGH)
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
      'Relay1b'  : relay1bSts,
      'Relay2b'  : relay2bSts,
      'Relay4b'  : relay4bSts,
      }
	return render_template('water.html', **templateData)
		
@app.route("/PUMPOFF")
def pumpoff():
	GPIO.output(relay1b, GPIO.LOW)
	GPIO.output(relay2b, GPIO.LOW)
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
      'Relay1b'  : relay1bSts,
      'Relay2b'  : relay2bSts,
      'Relay4b'  : relay4bSts,
      }		
	return render_template('water.html', **templateData)
	
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
