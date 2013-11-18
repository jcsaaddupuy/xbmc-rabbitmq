import time
import json
import xbmc

from config import Config
from pluginconfig import RmqConfig

import pika


# Log TAG
TAG="CLU XBMC - Notification Handler"

class NotificationHandler(object):
  _addon = None
  _channel = None
  _config = None
  _rmqconfig = None
  _policy = None

  def __init__(self, addon):
    self._addon = addon
    self._config = Config()
    self._rmqconfig = RmqConfig()
    self._connection = None
    self._channel = None

  def loadconfig(self):
    xbmc.log(msg="[%s] Obtaining config"%(TAG)) 
    self._config.load(self._addon, self._rmqconfig)

  def handle(self, objmessage):
    xbmc.log(msg="[%s] Handling message"%(TAG)) 
    xbmc.log(msg="[%s] Initialising message channel"%(TAG)) 
    self.loadconfig()

    try:
      self.initconnection()
      try:
        self.publish(objmessage)
        xbmc.log(msg="[%s] Success : Message posted"%(TAG))
      except Exception, ex2:
        xbmc.log(msg="[%s] Error : %s"%(TAG, ex2), level=xbmc.LOGERROR)
      self.disconnect()
    except Exception, ex:
      xbmc.log(msg="[%s] Error : %s"%(TAG, ex), level=xbmc.LOGERROR)

  def initconnection(self):
    cred=pika.PlainCredentials(self._rmqconfig.user, self._rmqconfig.password)
    params= pika.ConnectionParameters(host=self._rmqconfig.host, port=self._rmqconfig.port, credentials=cred)
    self._connection = pika.BlockingConnection(params)
    self._channel = self._connection.channel()

  def publish(self, objmessage):
    message=json.dumps(objmessage)
    channel = self._connection.channel()
    channel.basic_publish(exchange=self._rmqconfig.exchange, routing_key=self._rmqconfig.routing_key, body=message)

  def disconnect(self):
    self._connection.close()
