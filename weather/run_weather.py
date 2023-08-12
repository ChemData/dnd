from json import load
import sys
import getopt
from random import choice, choices
import numpy as np


with open('climates.json', 'r') as f:
    weather_tables = load(f)

generic_system_names = ['cold', 'normal', 'hot']

temp_descriptions = ['frigid < -15', 'freezing (-15-32)', 'cold (33-55)', 'cool (55-69)', 'warm (70-84)', 'hot (85-99)', 'scorching (100+)']
rain_descriptions = ['no', 'light', "moderate", "heavy"]
wind_descriptions = ['calm', "breezy", 'windy', 'blowing hard']

# Default Values
climate = 'metzuba'
season = 'winter'
weather = 'normal'

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'c:s:w:', ['climate=', 'season=', 'weather='])

for opt, arg in opts:
    if opt == '-c':
        climate = arg
    elif opt == '-s':
        season = arg
    elif opt == '-w':
        weather = arg
weather_systems_stats = weather_tables[climate][season]
system_num = generic_system_names.index(weather)
system_names = list(weather_systems_stats.keys())

transition_probs = [
    [0.4, 0.5, 0.1],
    [0.15, 0.7, 0.15],
    [0.1, 0.5, 0.4]]

while True:
    system_name = system_names[system_num]
    temp_num = choice(weather_systems_stats[system_name][0])
    temp = temp_descriptions[temp_num]
    precip_num = choice(weather_systems_stats[system_name][1])
    precip = rain_descriptions[precip_num]
    wind_num = choice(weather_systems_stats[system_name][2])
    wind = wind_descriptions[wind_num]

    if temp_num <= 1:
        precip_type = 'snow'
    else:
        precip_type = 'rain'

    print(f'The day is {temp} and {wind} with {precip} {precip_type}. [{system_name}]')

    camping_weather = 'normal'
    if wind_num >= 2 and precip_num >= 2:
        camping_weather = 'bad'
    if temp_num <= 1:
        camping_weather = 'bad'
    if precip_num == 3 and (wind_num == 3 or temp_num <= 1):
        camping_weather = 'extreme'
    if camping_weather != 'normal':
        print(f'Camping is made harder by the {camping_weather} weather.')

    if temp_num == 0:
        print('Extremely cold weather (DMG 110).')

    if temp_num == 6:
        print('Extremely hot weather (DMG 110).')

    if wind_num == 3:
        print('Strong wind (DMG 110).')

    if precip_num == 3:
        print('Strong Precipitation (DMG 110).')

    system_num = choices(range(len(transition_probs)), transition_probs[system_num])[0]
    input()
