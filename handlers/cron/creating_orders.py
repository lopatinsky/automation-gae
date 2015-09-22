import datetime

from google.appengine.api.namespace_manager import namespace_manager
from google.appengine.ext.ndb import metadata
from webapp2 import RequestHandler

from methods import alfa_bank, paypal
from methods.emails import admins
from models import Order
from models.order import CREATING_ORDER
from models.venue import Venue

MINUTES_INTERVAL = 10


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
                    infos.append(info)
                namespace_infos[namespace] = infos
        mail_body = "Orders with creating status\n"
        for namespace in namespace_infos.keys():
            mail_body += 'In namespace = %s:\n' % namespace
            mail_body += "List of orders:\n" + \
                         "\n\n".join("\n".join("%s: %s" % t for t in info) for info in namespace_infos[namespace])
        if namespace_infos:
            admins.send_error("order", "Orders crashed while creating", mail_body)
