#! /usr/bin/env python
# Copyright (c) 2010-2011 Magnus Olsson (magnus@minimum.se)
# See LICENSE for details
"""windspeak
This program reads WindWiz weatherdata for a given station using a set of 
prerecorded audio clips.

usage: windspeak [options]

options:
-u <url>	API root URL, defaults to http://vind.minimum.se/api/v3
-l		List all available stations
-s <station>	Station name, use -l to list available stations
-o <outfile>	Output wavefile. Defaults to 'windspeak.wav'
-v <voice>	Use <voice> for output. Defaults to 'magnus'
"""

import getopt
import sys
import subprocess
import simplejson as json
import urllib
import wave

def wavJoin(output, voice, parts):
	ow = wave.open(output, 'wb')
	ow.setnchannels(1)
	ow.setsampwidth(2)
	ow.setframerate(44100)
	for part in parts:
		iw = wave.open('voices/' + voice + '/' + part, 'rb')
		nframes = iw.getnframes()
		ow.writeframes(iw.readframes(nframes))
		iw.close()
	ow.close()

def getStationList(api):
	f = urllib.urlopen(api + "/index.json")
	return json.loads(f.read())

def getHistory(api, stationid):
	f = urllib.urlopen(api + "/" + stationid + "/history.json")
	return json.loads(f.read())

def intToWav(n):
	wavs = []
	if (n < 0):
		wavs.append("minus.wav")
		wavs.extend(intToWav(abs(n)))
	elif (n >= 0 and n <= 20):
		wavs.append(str(n) + ".wav")
	else:
		if (n > 100): 
			hundred = int(n / 100)
			wavs.append(str(hundred * 100) + "-.wav")
			wavs.extend(intToWav(n % 100))
		elif (n > 10):
			tens = int(n / 10)
			if (n % 10 != 0):
				wavs.append(str(tens*10) + "-.wav")
				wavs.extend(intToWav(n % 10))
			else:
				wavs.append(str(tens*10) + ".wav")
						
	return wavs

def numToWav(n):
	wavs = []
	
	i = int(n)
	f = int(round((n - i) * 10))
	wavs.extend(intToWav(i))
	if (f != 0):
		wavs.append("comma.wav")
		wavs.extend(intToWav(f))

	return wavs

def degreesToWav(deg):
	wavs = []
	deg = int(deg)
	
	wavs.extend(intToWav(deg))
	wavs.append("degrees.wav")

	return wavs

def compassToWav(dir):
	wavs = []
	
	if (dir > 348.75):
		wavs.append("north.wav")
	elif (dir > 326.25):
		wavs.append("north.wav")
		wavs.append("north-west.wav")
	elif (dir > 303.75):
		wavs.append("north-west.wav")
	elif (dir > 281.25):
		wavs.append("west.wav")
		wavs.append("north-west.wav")
	elif (dir > 258.75):
		wavs.append("west.wav")
	elif (dir > 236.25):
		wavs.append("west.wav")
		wavs.append("south-west.wav")		
	elif (dir > 213.75):
		wavs.append("south-west.wav")
	elif (dir > 191.25):
		wavs.append("south.wav")
		wavs.append("south-west.wav")
	elif (dir > 168.75):
		wavs.append("south.wav")
	elif (dir > 146.25):
		wavs.append("south.wav")
		wavs.append("south-east.wav")
	elif (dir > 123.75):
		wavs.append("south-east.wav")
	elif (dir > 101.25):
		wavs.append("east.wav")
		wavs.append("south-east.wav")
	elif (dir > 78.75):
		wavs.append("east.wav")
	elif (dir > 56.25):
		wavs.append("east.wav")
		wavs.append("north-east.wav")
	elif (dir > 33.75):
		wavs.append("north-east.wav")
	elif (dir > 22.5):
		wavs.append("north.wav")
		wavs.append("north-east.wav")
	else:
		wavs.append("north.wav")

	return wavs

def generateWave(output, voice, history):
	latest = history[0]
	wavs = []
	wavs.append("winddir.wav")
	wavs.extend(compassToWav(latest['winddir_avg']))
	wavs.extend(degreesToWav(latest['winddir_avg']))
	wavs.append("windspeed.wav")
 	wavs.extend(numToWav(latest['windspeed_avg']))
	wavs.append("ms.wav")
	wavJoin(output, voice, wavs);

def usage(*args):
        sys.stdout = sys.stderr
        print __doc__
        for msg in args: print msg
        sys.exit(2)

if __name__ == "__main__":
	station = None
	url = 'http://vind.minimum.se/api/v3'
	output = 'windspeak.wav'
	voice = 'magnus'

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'lu:s:o:v:')
	except getopt.error, msg:
		usage(msg)

	stationList = getStationList(url)

	for o, a in opts:
		if o == '-l': 			
			for s in stationList:
				print s['id']
			sys.exit(1)
		if o == '-u': 
			url = a
		if o == '-s':
			station = a	
		if o == '-o':
			output = a
		if o == '-v':
			voice = a

	if station == None:
		usage("No station specified")

	# Make sure station exists in index
	found = False
	for s in stationList:
		if s['id'] == station:
			found = True
			break

	if not found:
		usage("Specified station does not exist")

	history = getHistory(url, station)

	generateWave(output, voice, history)
