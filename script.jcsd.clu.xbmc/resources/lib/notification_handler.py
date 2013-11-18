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
    self._config.load(self._addon, self._mpdconfig)

  def handle(self, objmessage):
    xbmc.log(msg="[%s] Handling message"%(TAG)) 
    xbmc.log(msg="[%s] Initialising message channel"%(TAG)) 
    try:
      self.initconnection()
      try:
        self.publish(objmessage)
      except Exception, ex2:
        xbmc.log(msg="[%s] Error : %s"%(TAG, ex2))
      self.disconnect()
    except Exception, ex:
      xbmc.log(msg="[%s] Error : %s"%(TAG, ex))

  def initconnection(self):
    cred=pika.PlainCredentials(self._config.user, self._config.password)
    params= pika.ConnectionParameters(host=self._config.host, port=self._config.port, credentials=cred)
    self._connection = pika.BlockingConnection(params)
    self._channel = self.connection.channel()

  def publish(self, objmessage):
    message=json.dumps(objmessage)
    channel = self.rmqchannel()
    channel.basic_publish(exchange=self._config.exchange, routing_key=self._config.routing_key, body=message)

  def disconnect(self):
    self._connection.disconnect()
