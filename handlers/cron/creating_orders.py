import datetime

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext import ndb
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from methods import alfa_bank, paypal
from methods.emails import admins
from methods.proxy.resto.history import find_lost_order
from models import Order
from models.config.config import config, AUTO_APP, RESTO_APP
from models.order import CREATING_ORDER, NEW_ORDER
from models.venue import Venue

MINUTES_INTERVAL = 10


def _handle_auto(order):
    info = [
        ("id", order.key.id()),
        ("payment type", order.payment_type_id),
        ("payment id", order.payment_id)
    ]
    to_delete = False
    if order.has_card_payment:
        try:
            # check payment status
            legal = Venue.get_by_id(int(order.venue_id)).legal.get()
            status = alfa_bank.check_extended_status(legal.alfa_login, legal.alfa_password,
                                                     order.payment_id)["alfa_response"]
            info.append(("status check result", status))

            # if status check was successful:
            if str(status.get("errorCode", '0')) == '0':
                # money already deposited -- do not delete
                if status['orderStatus'] == 2:
                    info.append(("ERROR", "deposited"))
                # money approved -- reverse
                elif status['orderStatus'] == 1:
                    reverse_result = alfa_bank.reverse(legal.alfa_login, legal.alfa_password,
                                                       order.payment_id)
                    info.append(("reverse result", reverse_result))
                    if str(reverse_result.get('errorCode', '0')) == '0':
                        to_delete = True
                # any other status is OK to delete
                else:
                    to_delete = True
        except Exception as e:
            info.append(("exception", repr(e)))
    elif order.has_paypal_payment:
        try:
            # authorization exists (we have payment_id) and should be non-void
            void_success, void_error = paypal.void(order.payment_id)
            info.append(("void successful?", void_success))
            if void_success:
                to_delete = True
            else:
                info.append(("void error", void_error))
        except Exception as e:
            info.append(("exception", repr(e)))
    else:
        to_delete = True
    if to_delete:
        order.key.delete()
        info.append(("deleted", True))
    return info


def _handle_resto(order):
    info = [
        ("id", order.key.id()),
    ]
    iiko_uuid = order.extra_data.get("iiko_uuid")
    info.append(("iiko id", iiko_uuid))

    try:
        search_result = find_lost_order(iiko_uuid)
        info.append(("search result", search_result))
        if not search_result:
            info.append(("deleted", True))
            order.key.delete()
            return info

        order.number = search_result['number']
        order.status = search_result['status'] or NEW_ORDER

        old_key = order.key
        order.key = ndb.Key(Order, search_result['number'])
        order.put()
        old_key.delete()
        info.append(("found", True))
    except Exception as e:
        info.append(("exception", repr(e)))
    return info


class CheckCreatingOrdersHandler(RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=MINUTES_INTERVAL)
        namespace_infos = {}
        for namespace in metadata.get_namespaces():
            namespace_manager.set_namespace(namespace)
            orders = Order.query(Order.status == CREATING_ORDER, Order.date_created <= now - delta).fetch()
            if orders:
                infos = []
                for order in orders:
                    if config.APP_KIND == AUTO_APP:
                        info = _handle_auto(order)
                    elif config.APP_KIND == RESTO_APP:
                        info = _handle_resto(order)
                    else:
                        info = [("ERROR", "unknown APP_KIND")]
                    infos.append(info)
                namespace_infos[namespace] = infos
        mail_body = "Orders with creating status\n"
        for namespace in namespace_infos.keys():
            mail_body += 'In namespace = %s:\n' % namespace
            mail_body += "List of orders:\n" + \
                         "\n\n".join("\n".join("%s: %s" % t for t in info) for info in namespace_infos[namespace])
        if namespace_infos:
            namespace_manager.set_namespace('')
            admins.send_error("order", "Orders crashed while creating", mail_body)
