TITLE    = 'Channel Title'
PREFIX   = '/video/channelname'
ART      = 'art-default.jpg'
ICON     = 'icon-default.png'
STREAM_URL = 'http://smooth.ruv.cache.is/'


def Start(): # Initialize the plug-in

  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

# Setup the default attributes for the ObjectContainer
ObjectContainer.title1 = TITLE
ObjectContainer.view_group = 'List'
ObjectContainer.art = R(ART)

# Setup the default attributes for the other objects
DirectoryObject.thumb = R(ICON)
DirectoryObject.art = R(ART)
VideoClipObject.thumb = R(ICON)
VideoClipObject.art = R(ART)

#####################################################################
@handler(PREFIX, TITLE)
def MainMenu():

  oc = ObjectContainer()
  
  oc.add(VideoClipObject(
  url = STREAM_URL + "lokad/4897620R12.mp4",
  title = "Live",
  summary = "Skemmtilegt",
  thumb = Callback(Thumb, url=thumb),
#  duration = "",
#  originally_available_at = date
  ))
  
  
  
  return oc 

def Thumb(url):

  try: 
    data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
    return DataObject(data, 'image/jpeg')
  except:
    return Redirect(R(ICON)) 