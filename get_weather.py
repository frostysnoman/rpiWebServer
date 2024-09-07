import os
import requests
import json
import sqlite3
from datetime import datetime
import subprocess
now = datetime.now()
print(now)
conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')

def get_db_connection():
    conn = sqlite3.connect('/home/ty/ghouse/rpiWebServer/greenhouse.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_vtemps():
	conn = get_db_connection()
	valvestemp = conn.execute('SELECT temp FROM temps where loc = "Valves" and ID in (select max(ID) from temps where loc = "Valves"); ').fetchone()
	valvestemp_data = valvestemp['temp']
	print(valvestemp_data)
	conn.close()
	if valvestemp is None:
		abort(404)
	return valvestemp_data
	
def get_zonemoist():
		conn = get_db_connection()
		sql = 'SELECT moist_soil_1, moist_soil_2, moist_soil_3, moist_soil_4, temp_soil_1, temp_soil_2, temp_soil_3, temp_soil_4 FROM weather where ID in (select max(ID) from weather where moist_soil_2 is not null); '
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
		
units = 'imperial'
uniteSymbols = {
	'imperial': 'F',
	'metric': 'C',
	'kelvin': 'K'
}

response = requests.get('https://api.weatherlink.com/v2/current/8e957807-b9db-4797-bf3a-37a068244bf6?api-key=rbvsoxyyavgxgwbpe2k1nrklvlkb2wbd',headers={"X-Api-Secret": "ghsdkbymegqnmjzhneycg0mzck0wu7m1"})
#response = requests.get("https://api.weatherlink.com/v2/stations?api-key=rbvsoxyyavgxgwbpe2k1nrklvlkb2wbd", headers={"x-api-secret":"ghsdkbymegqnmjzhneycg0mzck0wu7m1"})

#print(response.content)
response_dict = json.loads(response.text)
data = response_dict["sensors"][0]
#print(response_dict)
for item in data:
		#print("key: ", item, "val: ", data[item])
		if item == "data":
			print(data[item][0])
			print(data[item][0]["moist_soil_2"])
			conn.execute("INSERT INTO weather (moist_soil_1, moist_soil_2, moist_soil_3, moist_soil_4, temp_soil_1, temp_soil_2, temp_soil_3, temp_soil_4) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (data[item][0]["moist_soil_1"], data[item][0]["moist_soil_2"], data[item][0]["moist_soil_3"], data[item][0]["moist_soil_4"], data[item][0]["temp_1"], data[item][0]["temp_2"], data[item][0]["temp_3"], data[item][0]["temp_4"]))
			conn.commit()
data2 = response_dict["sensors"][1]
for item2 in data2:
		if item2 == "data":
			print(data2[item2][0])
			conn.execute("INSERT INTO weather (wind_speed_hi_last_2_min, hum, wind_dir_at_hi_speed_last_10_min, wind_chill, rain_rate_hi_last_15_min_clicks, thw_index, wind_dir_scalar_avg_last_10_min, rain_size, uv_index, wind_speed_last, rainfall_last_60_min_clicks, wet_bulb, rainfall_monthly_clicks, wind_speed_avg_last_10_min, wind_dir_at_hi_speed_last_2_min, rainfall_daily_in, wind_dir_last, rainfall_daily_mm, rain_storm_last_clicks, rain_storm_last_start_at, rain_rate_hi_clicks, rainfall_last_15_min_in, rainfall_daily_clicks, dew_point, rainfall_last_15_min_mm, rain_rate_hi_in, rain_storm_clicks, rain_rate_hi_mm, rainfall_year_clicks, rain_storm_in, rain_storm_last_end_at, rain_storm_mm, wind_dir_scalar_avg_last_2_min, heat_index, rainfall_last_24_hr_in, rainfall_last_60_min_mm, rainfall_last_60_min_in, rain_storm_start_time, rainfall_last_24_hr_mm, rainfall_year_in, wind_speed_hi_last_10_min, rainfall_last_15_min_clicks, rainfall_year_mm, wind_dir_scalar_avg_last_1_min, temp, wind_speed_avg_last_2_min, solar_rad, rainfall_monthly_mm, rain_storm_last_mm, wind_speed_avg_last_1_min, thsw_index, rainfall_monthly_in, rain_rate_last_mm, rain_rate_last_clicks, rainfall_last_24_hr_clicks, rain_storm_last_in, rain_rate_last_in, rain_rate_hi_last_15_min_mm, rain_rate_hi_last_15_min_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ", (data2[item2][0]["wind_speed_hi_last_2_min"], data2[item2][0]["hum"], data2[item2][0]["wind_dir_at_hi_speed_last_10_min"], data2[item2][0]["wind_chill"], data2[item2][0]["rain_rate_hi_last_15_min_clicks"], data2[item2][0]["thw_index"], data2[item2][0]["wind_dir_scalar_avg_last_10_min"], data2[item2][0]["rain_size"], data2[item2][0]["uv_index"], data2[item2][0]["wind_speed_last"], data2[item2][0]["rainfall_last_60_min_clicks"], data2[item2][0]["wet_bulb"], data2[item2][0]["rainfall_monthly_clicks"], data2[item2][0]["wind_speed_avg_last_10_min"], data2[item2][0]["wind_dir_at_hi_speed_last_2_min"], data2[item2][0]["rainfall_daily_in"], data2[item2][0]["wind_dir_last"], data2[item2][0]["rainfall_daily_mm"], data2[item2][0]["rain_storm_last_clicks"], data2[item2][0]["rain_storm_last_start_at"], data2[item2][0]["rain_rate_hi_clicks"], data2[item2][0]["rainfall_last_15_min_in"], data2[item2][0]["rainfall_daily_clicks"], data2[item2][0]["dew_point"], data2[item2][0]["rainfall_last_15_min_mm"], data2[item2][0]["rain_rate_hi_in"], data2[item2][0]["rain_storm_clicks"], data2[item2][0]["rain_rate_hi_mm"], data2[item2][0]["rainfall_year_clicks"], data2[item2][0]["rain_storm_in"], data2[item2][0]["rain_storm_last_end_at"], data2[item2][0]["rain_storm_mm"], data2[item2][0]["wind_dir_scalar_avg_last_2_min"], data2[item2][0]["heat_index"], data2[item2][0]["rainfall_last_24_hr_in"], data2[item2][0]["rainfall_last_60_min_mm"], data2[item2][0]["rainfall_last_60_min_in"], data2[item2][0]["rain_storm_start_time"], data2[item2][0]["rainfall_last_24_hr_mm"], data2[item2][0]["rainfall_year_in"], data2[item2][0]["wind_speed_hi_last_10_min"], data2[item2][0]["rainfall_last_15_min_clicks"], data2[item2][0]["rainfall_year_mm"], data2[item2][0]["wind_dir_scalar_avg_last_1_min"], data2[item2][0]["temp"], data2[item2][0]["wind_speed_avg_last_2_min"], data2[item2][0]["solar_rad"], data2[item2][0]["rainfall_monthly_mm"], data2[item2][0]["rain_storm_last_mm"], data2[item2][0]["wind_speed_avg_last_1_min"], data2[item2][0]["thsw_index"], data2[item2][0]["rainfall_monthly_in"], data2[item2][0]["rain_rate_last_mm"], data2[item2][0]["rain_rate_last_clicks"], data2[item2][0]["rainfall_last_24_hr_clicks"], data2[item2][0]["rain_storm_last_in"], data2[item2][0]["rain_rate_last_in"], data2[item2][0]["rain_rate_hi_last_15_min_mm"], data2[item2][0]["rain_rate_hi_last_15_min_in"]))
conn.commit()
conn.close()
print('logged data')
moisture = get_zonemoist()
ts2 = moisture['temp_soil_2']
actuator = 'pondheater'	
if ts2 < 60:
	print('turning on pond heater')
	kasarun = "kasa --host 192.168.150.211 on --name "+actuator
	ko = subprocess.run(kasarun.split(), timeout=2000)
	print(ko)
else:
	print('turning off pond heater')
	kasarun = "kasa --host 192.168.150.211 off --name "+actuator
	ko = subprocess.run(kasarun.split(), timeout=2000)
	print(ko)
print('checked pond temp')
valvestemp_data = get_vtemps()
actuator = 'pipeheater'	
if valvestemp_data < 18:
	print('turning on pipe heater')
	kasarun = "kasa --host 192.168.150.211 on --name "+actuator
	ko = subprocess.run(kasarun.split(), timeout=2000)
	print(ko)

else:
	print('turning off pipe heater')
	kasarun = "kasa --host 192.168.150.211 off --name "+actuator
	ko = subprocess.run(kasarun.split(), timeout=2000)
	print(ko)

print('finished everything')
