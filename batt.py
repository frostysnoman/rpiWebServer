import logging
import configparser
import os
import sys
import sqlite3
import subprocess
from datetime import datetime
current_date_and_time = datetime.now()

from renogybt import BatteryClient, DataLogger, Utils

def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn
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
		print('no battdata')
		abort(404)
	return ([batt_current, batt_voltage, batt_rem_charge, batt_capacity])
	
def put_battdata(batt_data):
	conn = get_db_connection()
	print(batt_data)
	print(type(batt_data))
	print('putbattdata')
	if 'current' in batt_data:
		batt_current = batt_data['current']
	batt_voltage = batt_data['voltage']
	batt_rem_charge = batt_data['remaining_charge']
	batt_capacity = batt_data['capacity']
	conn.execute('INSERT INTO battdata (batt_current, batt_voltage, batt_rem_charge, batt_capacity) VALUES (?, ?, ?, ?)', (batt_current, batt_voltage, batt_rem_charge, batt_capacity))
	conn.commit()
	print('wrote to db')
	batt_data2 = get_battdata()
	print('batt_data_type',type(batt_data2))
	bcurrent = batt_data2[0]
	bvoltage = batt_data2[1]
	brc = batt_data2[2]
	bcap = batt_data2[3]
	actuator = 'charger'
	if brc < 80:
		print('Current charge is : ',brc)
		kasarun = "kasa --host 192.168.150.211 on --name "+actuator
		subprocess.run(kasarun.split())
	else:
		print('Current charge is :',brc)
		kasarun = "kasa --host 192.168.150.211 off --name "+actuator
		subprocess.run(kasarun.split())
	pass



#logging.basicConfig(level=logging.DEBUG)

config_file = sys.argv[1] if len(sys.argv) > 1 else 'config.ini'
config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), config_file)
config = configparser.ConfigParser(inline_comment_prefixes=('#'))
config.read(config_path)
#data_logger: DataLogger = DataLogger(config)

# the callback func when you receive data
def on_data_received(client, data):
	filtered_data = Utils.filter_fields(data, config['data']['fields'])
	print('odr')
	print(filtered_data)
	put_battdata(filtered_data)
	
	print('finished odr')
	client.disconnect()
	pass
	
print(current_date_and_time)
print('calling client')
BatteryClient(config, on_data_received).connect()
dbus.connection.close()
print('finished')
sys.exit('data written')
