# coding=utf-8
from datetime import datetime
from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler
from methods.emails import admins
from models import Promo, STATUS_UNAVAILABLE, STATUS_AVAILABLE

__author__ = 'dvpermyakov'


class UpdatePromosHandler(RequestHandler):
    def get(self):
        result_text = u''
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            text = u''
            for promo in Promo.query().fetch():
                if promo.status == STATUS_AVAILABLE:
                    if promo.end and datetime.utcnow() >= promo.end:
                        promo.status = STATUS_UNAVAILABLE
                        promo.put()
                        text += u'\nАкция "%s" была выключена' % promo.title
                if promo.status == STATUS_UNAVAILABLE:
                    if promo.start and promo.start <= datetime.utcnow():
                        if promo.end and datetime.utcnow() >= promo.end:
                            continue
                        promo.status = STATUS_AVAILABLE
                        promo.visible = True
                        promo.put()
                        text += u'\nАкция "%s" была включена' % promo.title
            if text:
                result_text += u'В компании %s: %s' % (namespace, text)
        if result_text:
            namespace_manager.set_namespace('')
            admins.send_error('Promos', 'Promos has been updated', result_text)
