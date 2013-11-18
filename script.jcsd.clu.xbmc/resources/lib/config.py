

class Config:
    def load(self, addon, rmqconfig):
        rmqconfig.host = addon.getSetting('host')    
        rmqconfig.port = int(addon.getSetting('port'))
        rmqconfig.user = addon.getSetting('user')
        rmqconfig.password = addon.getSetting('password')

        rmqconfig.exchange = addon.getSetting('exchange')
        rmqconfig.type = addon.getSetting('type')
        rmqconfig.routing_key = addon.getSetting('routing_key')
