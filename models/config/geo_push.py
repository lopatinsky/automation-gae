import logging
from google.appengine.ext import ndb
from methods.rendering import timestamp
from models import STATUS_AVAILABLE, STATUS_CHOICES, Order
from models.config.config import GEO_PUSH_MODULE

__author__ = 'dvpermyakov'


class GeoPoint(ndb.Model):
    location = ndb.GeoPtProperty(required=True)
    radius = ndb.IntegerProperty(required=True)

    def dict(self, index):
        return {
            'id': str(index),
            'lat': self.location.lat,
            'lon': self.location.lon,
            'radius': self.radius
        }


class GeoPushModule(ndb.Model):
    status = ndb.IntegerProperty(default=STATUS_AVAILABLE, choices=STATUS_CHOICES)
    text = ndb.StringProperty(required=True)
    head = ndb.StringProperty(required=True)
    days_without_order = ndb.IntegerProperty(required=True)
    days_without_push = ndb.IntegerProperty(required=True)
    points = ndb.StructuredProperty(GeoPoint, repeated=True)

    def dict(self, client=None):
        logging.info(client)
        last_order = None
        last_order_timestamp = 0
        if client:
            last_order = Order.query(Order.client_id == client.key.id()).order(-Order.date_created).get()
            logging.info(last_order)
            if last_order:
                last_order_timestamp = timestamp(last_order.date_created)
        return {
            'type': GEO_PUSH_MODULE,
            'enable': self.status == STATUS_AVAILABLE,
            'info': {
                'head': self.head,
                'text': self.text,
                'days_without_order': self.days_without_order,
                'days_without_push': self.days_without_push,
                'last_order': last_order is not None,
                'last_order_timestamp': last_order_timestamp,
                'points': [point.dict(index) for index, point in enumerate(self.points)]
            }
        }
