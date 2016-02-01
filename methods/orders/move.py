import webapp2
from webapp2_extras import jinja2

from methods.orders.create import send_venue_email, send_venue_sms


def move_order(order, venue):
    if order.venue_id == str(venue.key.id()):
        return

    order.venue_id = str(venue.key.id())
    order.put()

    req = webapp2.get_request()
    renderer = jinja2.get_jinja2()
    send_venue_email(venue, order, req.host_url, renderer, move=True)
    send_venue_sms(venue, order, move=True)
