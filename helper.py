from google.appengine.api import namespace_manager

from models.config.config import Config, MINIMIZED

from google.appengine.ext.remote_api import remote_api_stub


remote_api_stub.ConfigureRemoteApiForOAuth('your_app_id.appspot.com',
                                           '/_ah/remote_api')
namespace_manager.set_namespace("tashir")
config = Config.get()
config.ORDER_EMAIL_FORMAT_TYPE = MINIMIZED
config.put()

