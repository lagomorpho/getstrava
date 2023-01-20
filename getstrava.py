#!/usr/bin/env python

import urllib.request
import json
import xmltodict
import re
import math
import os
import datetime

# change directory to script directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

kmtomi = 0.621371
mtoft = 3.28084


def parseDescription(description):
	data = {}

	splitDescription = description.split(', ')

	# this is for run
	# gotta do elliptical

	
	# Run: Distance: 4.2km, 
	(type, strDistance, distanceKm) = splitDescription[0].split(': ')
	distance = float(re.sub("[^0-9.]", '', distanceKm)) * kmtomi
	data['type'] = type
	data['distance'] = distance
	
	# Elevation Gain: 25m
	elevationGainM = re.sub("[^0-9.]", '', splitDescription[1].split(': ')[1])
	elevationGain = float(elevationGainM) * mtoft
	data['elevationGain'] = elevationGain
	
	# Moving Time: 00:34:04
	movingTime = splitDescription[2].split(': ')[1]	
	data['movingTime'] = movingTime
	(hours, mins, secs) = movingTime.split(':')
	durationSecs = int(secs) + (int(mins) * 60) +  (int(hours) * 60 * 60)
	data['durationSecs'] = durationSecs
	
	if type == "Run":
		# Pace: 8:02/km
		paceKm = splitDescription[3].split(': ')[1].split('/')[0]
		(minsKm, secsKm) = paceKm.split(':')
		totalsecs = math.floor((60 * int(minsKm)) + int(secsKm)) / kmtomi)
		mins = math.floor(totalsecs/60)
		secs = totalsecs % 60
		pace = "{:02d}:{:02d}".format(mins, secs)
		
		data['pace'] = pace
	elif type == "Elliptical":
		# Average Speed: 0.0km/h
		avgSpeed = float(re.sub("[^0-9.]", '', splitDescription[3].split(': ')[1])) * kmtomi
		data['avgSpeed'] = avgSpeed
	
	return data


def getMarkdownFiles():
	files = os.listdir('.')
	mdfiles = []
	for file in files:
		if file.endswith('.md'):
			mdfiles.append(file)

	return files


def activityExists(uid):
	mdFiles = getMarkdownFiles()
	for file in mdFiles:
		if uid in file:
			return True
	
	return False
		


def main():

	url = 'https://feedmyride.net/activities/64695128'
	with urllib.request.urlopen(url) as response:
		html = response.read()
	
	xml = html.decode("utf-8")
	jsonfeed = xmltodict.parse(xml)

# 	open('rss.json', 'w').write(json.dumps(jsonfeed))
	
	for activity in jsonfeed["rss"]["channel"]["item"]:
		activityData = parseDescription(activity["description"])
		activityData['lat'] = activity['geo:lat']
		activityData['long'] = activity['geo:long']
		activityData['date'] = activity['pubDate']
		activityData['title'] = activity['title']
		activityData['link'] = activity['link']
		activityData['uid'] = activity['link'].split('/')[-1]
		
		if not activityExists(activityData['uid']):
			# Thu, 19 Jan 2023 14:12:13 -0800
			activityDatetime = datetime.datetime.strptime(activityData['date'], "%a, %d %b %Y %H:%M:%S %z")
			activityDate = activityDatetime.isoformat()
			filename = "%s %0.2f mile %s %s.md" % (activityDate[:10], activityData['distance'], activityData['type'], activityData['uid'])
			
			print(filename)
			file = open(filename, 'w')
			file.write("---\n")
			
			for key, val in activityData.items():
				file.write("%s: %s\n" % (key, val))
			
			file.write("timestamp: %s\n" % (activityDate))
			file.write("isodate: %s\n" % (activityDate[:10]))
			file.write("---\n")
			file.write("# %0.2f mile %s\n" % (activityData['distance'], activityData['type']))
# 			file.write("Date:: %s\n" % (activityDate[:10]))
# 			file.write("Distance:: %s miles\n" % (activityData['distance']))
# 			file.write("Duration:: %s\n" % (activityData['movingTime']))
# 			file.write("Pace:: %s min/mile\n" % (activityData['pace']))
# 			file.write("\n")

			if activityData['type'] == 'Run':
				file.write("|Date|Distance|Duration|Pace|\n")
				file.write("|----|--------|--------|----|\n")
				file.write("|%s|%0.2f miles|%s|%s min/mile|\n" % (activityDate[:10], activityData['distance'], activityData['movingTime'], activityData['pace']))
			elif activityData['type'] == 'Elliptical':
				file.write("|Date|Distance|Duration|Average Speed|\n")
				file.write("|----|--------|--------|-------------|\n")
				file.write("|%s|%0.2f miles|%s|%s min/mile|\n" % (activityDate[:10], activityData['distance'], activityData['movingTime'], activityData['avgSpeed']))
			file.write("Workout:: \n")
			file.write("Route:: \n")
			file.write("\n")

			file.write("## Notes\n")
			file.write("- \n")
			
			file.close()


if __name__ == '__main__':
	main()