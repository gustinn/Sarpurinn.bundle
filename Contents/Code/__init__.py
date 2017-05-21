import datetime

TITLE    = 'Sarpurinn'
PREFIX   = '/video/sarpurinn'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
STREAM_URL = 'http://smooth.ruv.cache.is'
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

@route(PREFIX + '/createvideoclipobject', include_container = bool)
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
						key = HTTPLiveStreamURL(Callback(PlayVideo, url = url))
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
@route(PREFIX + '/playvideo.m3u8')
def PlayVideo(url):
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
	
@route(PREFIX, "/schedule")
def Schedule(day):
	
	return None
	
@route(PREFIX, "/daysmenu")
def DaysMenu():
	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(SarpMenu), title= unicode("Í dag")))
	
	for d in range(1,SARP_STOR_DAYS+1):
		dagur = datetime.date.today() - datetime.timedelta(days=d)
		oc.add(DirectoryObject(key=Callback(Day, dags = str(dagur)), title=str(dagur)))
	return oc
	
@route(PREFIX, "/day")
def Day(dags):
	oc = ObjectContainer()
	oc.title2 = dags
	
	return oc

@route(PREFIX, "/sarpmenu")
def SarpMenu():
	oc = ObjectContainer()
	oc.add(DirectoryObject(key=Callback(DaysMenu), title="Fyrri dagar", thumb = R(ICON)))
	oc.add(VideoClipObject(
		url = STREAM_URL + "/lokad/4897620R12.mp4",
		title = "Rembrandt",
		summary = "Skemmtilegt",
		thumb = R(ICON), #Callback(Thumb, url=thumb),
		duration = 5*60*1000,
		#  originally_available_at = date
		)
	)
	
	return oc


  
def Thumb(url):

  try: 
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON)) 