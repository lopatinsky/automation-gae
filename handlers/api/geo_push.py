from handlers.api.base import ApiHandler
from models import Client, STATUS_AVAILABLE
from models.geo_push import GeoPush

__author__ = 'dvpermyakov'


class AddPushHandler(ApiHandler):
    def post(self):
        client_id = int(self.request.headers.get('Client-Id') or 0)
        if not client_id:
            self.abort(400)
        client = Client.get(client_id)
        if not client:
            self.abort(400)
        push = GeoPush.query(GeoPush.client == client.key, GeoPush.status == STATUS_AVAILABLE).order(-GeoPush.created).get()
        if not push:
            push = GeoPush(client=client.key)
            push.put()
        self.render_json({
            'success': True
        })
