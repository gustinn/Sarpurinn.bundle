# -*- coding: utf-8 -*-
import datetime
from xml.etree import ElementTree
import urllib
import json

TITLE    = 'Sarpurinn'
PREFIX   = '/video/sarpurinn'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
STREAM_URL = 'http://smooth.ruv.cache.is/'
INFO_URL = "http://ruv.is/sarpurinn"
SARP_STOR_DAYS = 31


def Start(): # Initialize the plug-in

  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

# Setup the default attributes for the ObjectContainer
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'Details'
  ObjectContainer.art = R(ART)

# Setup the default attributes for the other objects
#DirectoryObject.thumb = R(ICON)
#DirectoryObject.art = R(ART)
#VideoClipObject.thumb = R(ICON)
#VideoClipObject.art = R(ART)

#####################################################################
@handler(PREFIX, TITLE)
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key=Callback(LiveMenu), title="Live", thumb = R(ICON)))
  oc.add(DirectoryObject(key=Callback(SarpMenu), title="Sarpurinn", thumb = R(ICON)))
  
  return oc 

@route(PREFIX + '/createliveobject', include_container = bool)
def CreateLiveObject(url, title, summary, thumb = None, vidCodec = None, audCodec = None, media_container = None, vidRes = None, include_container=False, *args, **kwargs):
	
	video_object = VideoClipObject(
		key = Callback(CreateLiveObject, url = url, title = title, summary = summary, thumb = thumb, vidCodec = vidCodec, audCodec = audCodec, media_container = media_container, vidRes = vidRes, include_container = True),
		rating_key = url, ### ???????
		title = title,
		summary = summary,
		thumb = thumb,
		items = [
			MediaObject(
				parts = [
					PartObject(
						key = HTTPLiveStreamURL(Callback(PlayVideoLive, url = url))
					)
				],
				video_codec = vidCodec, #VideoCodec.H264,
				audio_codec = audCodec, #AudioCodec.AAC,
				video_resolution = vidRes,
				audio_channels = 2,
				container = media_container, #Container.MP4,
				optimized_for_streaming = True
			)
		]
	)
	
	if include_container:
		return ObjectContainer(objects = [video_object])
	else:
		return video_object

@indirect
@route(PREFIX + '/playvideolive.m3u8')
def PlayVideoLive(url):
	return IndirectResponse(VideoClipObject, key=url)
	
@route(PREFIX, "/livemenu")
def LiveMenu():
	oc = ObjectContainer()
	oc.add(CreateLiveObject(
		url = "http://ruvruv-live.hls.adaptive.level3.net/ruv/ruv/index/stream4.m3u8",
		title = "RÚV",
		summary = "Bein útsending RÚV",
		thumb = R("ruv.png"), #Callback(Thumb, url=thumb),
		vidCodec = VideoCodec.H264,
		audCodec = AudioCodec.AAC,
		media_container = Container.MP4,
		vidRes = "720",
		include_container=False
		)
	)
	oc.add(CreateLiveObject(
		url = "http://ruvruv2-live.hls.adaptive.level3.net/ruv/ruv2/index/stream5.m3u8",
		title = "RÚV 2",
		summary = "Bein útsending RÚV 2",
		thumb = R("ruv2.png"), #Callback(Thumb, url=thumb),
		vidCodec = VideoCodec.H264,
		audCodec = AudioCodec.AAC,
		media_container = Container.MP4,
		vidRes = "1080",
		include_container=False
		)
	)
	return oc

@route(PREFIX + '/createvideoobject', include_container = bool)
def CreateVideoObject(url, title, summary, thumb = None, vidCodec = None, audCodec = None, media_container = None, vidRes = None, include_container=False, *args, **kwargs):
	
	video_object = VideoClipObject(
		key = Callback(CreateLiveObject, url = url, title = title, summary = summary, thumb = thumb, vidCodec = vidCodec, audCodec = audCodec, media_container = media_container, vidRes = vidRes, include_container = True),
		rating_key = url, ### ???????
		title = title,
		summary = summary,
		thumb = thumb,
		items = [
			MediaObject(
				parts = [
					PartObject(
						key = HTTPLiveStreamURL(Callback(PlaySarpVideo, url = url))
					)
				],
				video_codec = vidCodec, #VideoCodec.H264,
				audio_codec = audCodec, #AudioCodec.AAC,
				video_resolution = vidRes,
				audio_channels = 2,
				container = media_container, #Container.MP4,
				optimized_for_streaming = True
			)
		]
	)
	
	if include_container:
		return ObjectContainer(objects = [video_object])
	else:
		return video_object

@indirect
@route(PREFIX + '/playsarpvideo')
def PlaySarpVideo(url):
	vid_url = ""
	for nr in range(30):
		url_test = url + "R" + str(nr) + ".mp4"
		Log("URL TEST: "+url_test)
		if (urllib.urlopen(url_test).getcode() == 200):
			vid_url = url_test
			break
	if (vid_url == ""):
		Log("Not found on server")
		return None
	
	Log(vid_url)
	return IndirectResponse(VideoClipObject, key=vid_url)

# Get the TV schedule for specified day
@route(PREFIX, "/getschedule")
def GetSchedule(dags):
	schedule = {}
	#schedule['date'] = datetime.date.today()
	
	url = "http://muninn.ruv.is/files/xml/ruv/" + dags + "/"
	r = urllib.urlopen(url)
	if (r.getcode() != 200):
		print "Could not get schedule"
		return None
	schedule_xml = ElementTree.fromstring(r.read())
	
	if (schedule_xml is None):
		print "Could not get schedule"
		return None
	
	for child in schedule_xml.iter("service"):
		# if (not child.tag == "service"):
		#	continue
		#Log(child)
		for entry_xml in child.iter('event'):
			entry = {}
			entry['title'] = entry_xml.find('title').text
			entry['pid'] = entry_xml.get('event-id')
			entry['showtime'] = entry_xml.get('start-time')
			entry['duration'] = entry_xml.get('duration')
			entry['sid'] = entry_xml.get('serie-id')
			
			# find if iceland only
			isl = entry_xml.get('mark')
			if (isl == "yes"):	
				entry['isl'] = True
			elif( isl == "no"):
				entry['isl'] = False
			else: 
				entry['isl'] = None
			
			details_basic = entry_xml.find('description')
			if( not details_basic is None):
				entry['desc'] = details_basic.text
			
			entry_org_title = entry_xml.find('original-title')
			if( not entry_org_title is None ):
				entry['original-title'] = entry_org_title.text
			
			# If the series id is nothing then it is not a show (e.g. dagskrárlok)
			if( not entry['sid'] ):
				continue
			
			cat = entry_xml.find('category')
			if(  not cat is None  ):
				entry['catid'] = cat.get('value')
				entry['cat'] = cat.text
			
			ep = entry_xml.find('episode')
			if( not ep is None ):
				entry['ep_num'] = ep.get('number')
				entry['ep_total'] = ep.get('number-of-episodes')
			if( int(entry['ep_total']) > 1 ):
				# Append the episode number to the show title if it is a real multi-episode show
				entry['title'] = entry['title'] + " ("+entry['ep_num']+" af "+entry['ep_total']+")"
			else:
				# If it isn't a multi episode show then append the date to the title (to avoid overwriting files)
				entry['title'] = str(entry['title'])+ " (" + entry['showtime'][:16] + ")"
			
			schedule[entry['pid']] = entry
	return schedule
	
@route(PREFIX, "/daysmenu")
def DaysMenu():
	oc = ObjectContainer()
	oc.title1 = TITLE
	oc.title2 = unicode("Veldu dag")
	oc.add(DirectoryObject(key=Callback(SarpMenu), title= unicode("Í dag")))
	
	for d in range(1,SARP_STOR_DAYS+1):
		dagur = datetime.date.today() - datetime.timedelta(days=d)
		oc.add(DirectoryObject(key=Callback(SarpMenu, dags = str(dagur)), title=str(dagur)))
	return oc
	
@route(PREFIX, "/sarpmenu")
def SarpMenu(dags = None):
	other = "Fyrri dagar"
	if dags is not None:
		other = unicode("Aðrir dagar")
	else:
		dags = str(datetime.date.today())
	
	# get schedule
	schedule = GetSchedule(dags)
	#schedule = sorted(schedule, key=itemgetter('showtime'), reverse=True)
	oc = ObjectContainer()
	oc.title2 = dags
	oc.add(DirectoryObject(key=Callback(DaysMenu), title=other, thumb = R(ICON)))
	Log(len(schedule.items()))
	for key, schedule_item in schedule.items():
		if (not 'pid' in schedule_item):
			continue
		titill = schedule_item['title']
		#date = datetime.datetime.strptime(schedule_item['showtime'], '%Y-%m-%d %H:%M:%S')
		desc = schedule_item["desc"]
		#duration = schedule_item["duration"]
		pid = schedule_item["pid"]
		preUrl = "opid/"
		Log(pid)
		if (schedule_item['isl']):
			preUrl = "lokad/"
		
		oc.add(CreateVideoObject(
			url = STREAM_URL + preUrl + pid,
			title = titill,
			summary = desc,
			thumb = R(ICON), #Callback(Thumb, url=thumb),
			vidCodec = VideoCodec.H264,
			audCodec = AudioCodec.AAC,
			media_container = Container.MP4,
			vidRes = "720",
			include_container=False
			)
		)
		
	
	# oc.add(VideoClipObject(
		# url = STREAM_URL + "lokad/4897620",
		# title = "Rembrandt",
		# summary = "Skemmtilegt",
		# thumb = R(ICON), #Callback(Thumb, url=thumb),
		# duration = 5*60*1000,
		# #  originally_available_at = date
		# )
	# )
	
	return oc


  
def Thumb(url):

  try: 
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON)) 