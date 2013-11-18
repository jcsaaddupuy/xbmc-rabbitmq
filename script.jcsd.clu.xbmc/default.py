import sys, os
import xbmcaddon, xbmc


# Log TAG
TAG="CLU XBMC"

__scriptid__ = 'script.jcsd.clu.xbmc'
xbmc.log(msg="[%s] %s loaded" % (TAG, __scriptid__), level=xbmc.LOGERROR)

__addon__ = xbmcaddon.Addon(id=__scriptid__)
sys.path.append(os.path.join (__addon__.getAddonInfo('path'), 'resources', 'lib'))

xbmc.log(msg="[%s] %s started" % (TAG, __scriptid__), level=xbmc.LOGERROR)


from notification_handler import NotificationHandler
from notification_service import NotificationService

mpdh = NotificationHandler(__addon__)
ns = NotificationService(mpdh)

ns.start()
ns.join()
xbmc.log(msg="[%s] %s stopped" % (TAG, __scriptid__))
