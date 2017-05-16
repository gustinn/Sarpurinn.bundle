TITLE    = 'Sarpurinn'
PREFIX   = '/video/sarpurinn'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
STREAM_URL = 'http://smooth.ruv.cache.is'
INFO_URL = "http://ruv.is/sarpurinn"


def Start(): # Initialize the plug-in

  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

# Setup the default attributes for the ObjectContainer
  ObjectContainer.title1 = TITLE
  ObjectContainer.view_group = 'List'
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
  oc.add(DirectoryObject(key=Callback(LiveMenu), title="Live"))
  oc.add(VideoClipObject(
    #url = "https://pastebin.com/raw/upg1RfuJ",
    url = STREAM_URL + "/lokad/4897620R12.mp4",
    title = "Rembrandt",
    summary = "Skemmtilegt",
    thumb = R(ICON), #Callback(Thumb, url=thumb),
    duration = 5*60*1000,
    #  originally_available_at = date
    )
  )
  
  
  
  return oc 

@route(PREFIX, "/livemenu")
def LiveMenu():
	oc = ObjectContainer()
	oc.add(VideoClipObject(
		url = STREAM_URL + "/lokad/4897620R12.mp4",
		title = "Rembrandt",
		summary = "Skemmtilegt",
		thumb = R(ICON), #Callback(Thumb, url=thumb),
		duration = 100000,
		#originally_available_at = date
		)
	)
  
  
def Thumb(url):

  try: 
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON)) 