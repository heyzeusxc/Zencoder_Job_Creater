"""
This jawn will create a Zencoder job with 8 outputs, with various settings, and update a pre-made .smil file with the new output destinations.
First we'll import the modules we need.
"""

import os
import sys
from zencoder import Zencoder
from ftplib import FTP

print ''

#Set your API Key for Zencoder here

client = Zencoder('***API KEY***')

#These are temporary bins to hold some data

bin = []
new_file = []

"""
OutputMaker is a function that will create the output settings for Zencoder when we tell it to make the job.
The regular arguments are in every output setting, the **kwargs are just for a few outputs with extra settings.
"""

def OutputMaker(label, event_length, reconnect_time, size, vbr, abr, live, **kwargs):
	output = {}
	output.update({
		"label": label,
		"event_length": event_length,
		"reconnect_time": reconnect_time,
		"size": size,
		"video_bitrate": vbr,
		"audio_bitrate": abr,
		"live_stream": live,
		})
	if 'mfr' in kwargs:
		output["max_frame_rate"] = kwargs['mfr']
	if 'type' in kwargs:
		output["type"] = kwargs['type']
	if 'streams' in kwargs:
		output["streams"] = [{"bandwidth": 396, "path": "hls396/index.m3u8"}, {"bandwidth": 496, "path": "hls496/index.m3u8"}, {"bandwidth": 596, "path": "hls596/index.m3u8"}]
	return output

print 'Creating Zencoder Job...'

#The next step creates the job with all the settings we need

create = client.job.create(
		live_stream = True,
		outputs =[
				OutputMaker("rtmp596", 10800, 1800, "1264x710", 500, 96, True),
			
				OutputMaker("rtmp396", 10800, 1800, "1264x710", 300, 64, True, mfr=15),

				OutputMaker("rtmp496", 10800, 1800, "768x432", 400, 96, True),
		
				OutputMaker("rtmp296", 10800, 1800, "768x432", 200, 64, True, mfr=15),

				OutputMaker("hls396", 10800, 1800, "1264x710", 300, 96, True, mfr=15),

				OutputMaker("hls496", 10800, 1800, "768x432", 400, 96, True, type="segmented"),

				OutputMaker("hls596", 10800, 1800, "1264x710", 500, 96, True, type="segmented"),

				OutputMaker("hlsmaster", 10800, 1800, "768x432", 400, 96, True, type="playlist", streams=True)
			]
		)

print 'Zencoder Job Created'
print 'Sorting Job Data...'

"""
Here is where the first data bin comes into play.
This just gets the data we need from the API response and stores each output's label, id, and URL together.
"""

stream_name = create.body['stream_name']

stream_id = create.body['id']

for x in create.body['outputs']:
	temp = []
	temp.append(str(x['label']))
	temp.append(str(x['id']))
	temp.append(str(x['url']))
	bin.append(temp)

print 'Job Data Sorted'

print 'Opening RTMP File...'

"""
In this 'with open' section, the original .smil file is opened, scanned, and updates the new URL's.
The bin we used in the last section is used to check that the right URL is matched with the right label.
Each line of the original file with the new updated URL's is then stored in the 'new_file' bin.
"""

with open('***FILE PATH***','r+') as rtmpFile:
	print 'File Opened'
	print 'Reading File'
	for x in rtmpFile:
		if '<video' in x:
			#print x[:-1]
			url_start = x.find('src="') + 5
			old_rtmp = x[url_start:x.find('"',url_start + 1)]
			for y in bin[:4]:
				if y[0][len(y[0])-3:] in x:
					new_rtmp = y[2][::-1][:y[2][::-1].find('/')][::-1]
					x = x.replace(old_rtmp,new_rtmp)
		new_file.append(x)
	rtmpFile.close()

print 'File Read'
print 'Updating File...'

#Here is where the new .smil file is actually written using the 'new_file' data to write the lines.

with open('***FILE PATH***','w') as newRTMPfile:
	for z in new_file:
		newRTMPfile.write(z)
	newRTMPfile.close()

print 'File Updated'
print 'Connecting to FTP'

#This last section connects to the FTP server where the .smil file will be uploaded.

ftp = FTP('***FTP ADDRESS***')

print 'Logging In...'

ftp.login('***USER***','***PASSWORD***')

print 'Logged In'

print 'Navigating FTP Directory...'

ftp.cwd('***DIRECTORY***')

print 'FTP Navigation Completed'
print 'Uploading File...'

file = ***FILE PATH***
upload = open(file,'rb')
ftp.storbinary('STOR ***FILE NAME***', upload)

print 'File Uploaded'

ftp.quit()

print 'FTP Connection Closed'	


