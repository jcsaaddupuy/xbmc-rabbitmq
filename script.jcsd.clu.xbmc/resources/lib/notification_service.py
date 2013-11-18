# -*- coding: utf-8 -*-
''' Handles notifications from XBMC via its own thread and forwards them on to the handler '''

''' 
    Script heavily inspired by the notification services presents in script.trakt and script.TrackUtilities
    all credits to theirs respectives authors 
'''
import xbmc
import telnetlib
import socket
import simplejson as json
import threading
from time import sleep


# Log TAG
TAG='CLU XBMC - Notification Handler'

class NotificationService(threading.Thread):
  ''' Receives XBMC notifications and passes them off as needed '''
  TELNET_ADDRESS = 'localhost'
  TELNET_PORT = 9090
  _maxConnectionTry = 20
  _connectionWaitRetry = 2
  _abortRequested = False
  _handler = None
  _notificationBuffer = ''

  def __init__(self, handler):
    self._handler = handler
    threading.Thread.__init__(self)

  def _forward(self, notification):
    ''' Fowards the notification recieved to a function on the scrobbler '''
    try:
      self.handler.handle(notification)
    except Exception , e :
      xbmc.log(msg='[%s] Error whith handler : %s' % (e), level=xbmc.LOGERROR)

  def _readNotification(self, telnet):
    ''' Read a notification from the telnet connection, blocks until the data is available, or else raises an EOFError if the connection is lost '''
    while not (self._abortRequested or xbmc.abortRequested):
      try:
        addbuffer = telnet.read_some()
      except socket.timeout:
        continue

      if addbuffer == '':
        raise EOFError

      self._notificationBuffer += addbuffer
      try:
        data, offset = json.JSONDecoder().raw_decode(self._notificationBuffer)
        self._notificationBuffer = self._notificationBuffer[offset:]
      except ValueError:
        continue
      except Exception , e:
        xbmc.log(msg=e, level=xbmc.LOGSEVERE)
        break
      return data


  def run(self):
    tried = 0
    xbmc.log(msg='[%s] Notification service started'%(TAG))
    #while xbmc is running
    telnet = None
    while not (self._abortRequested or xbmc.abortRequested):
      try:
        telnet = telnetlib.Telnet(self.TELNET_ADDRESS, self.TELNET_PORT)
      except IOError, e:
        tried = tried + 1
        xbmc.log(msg='[%s]  Telnet too soon? : %s ' % (TAG, e), level=xbmc.LOGSEVERE)
        if tried < self._maxConnectionTry:
          sleep(self._connectionWaitRetry)
          continue
        else:
          xbmc.log('[%s]  Could not establish connection after %i attemps. Shutdown' % (TAG, tried), level=xbmc.LOGFATAL)
          break
        xbmc.log(msg='[%s] Telnet service created'%(TAG))
        while not (self._abortRequested or xbmc.abortRequested):
          try:
            data = self._readNotification(telnet)
            self._forward(data)
          except EOFError:
            telnet = telnetlib.Telnet(self.TELNET_ADDRESS, self.TELNET_PORT)
            self._notificationBuffer = ''
            continue
          except Exception, e:
            xbmc.log(msg=e, level=xbmc.LOGSEVERE)
            break
    if telnet is not None:
      telnet.close()
    xbmc.log(msg='[%s] Notification service stopped'%(TAG))
