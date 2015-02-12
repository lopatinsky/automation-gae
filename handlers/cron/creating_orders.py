import datetime
import webapp2
from methods import email, alfa_bank
from models import CREATING_ORDER, Order, CARD_PAYMENT_TYPE


class CheckCreatingOrdersHandler(webapp2.RequestHandler):
    def get(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=2)
        orders = Order.query(Order.status == CREATING_ORDER, Order.date_created <= now - delta).fetch()
        if not orders:
            return

        infos = []

        for order in orders:
            info = [
                ("id", order.key.id()),
                ("payment type", order.payment_type_id),
                ("payment id", order.payment_id)
            ]
            to_delete = False
            if order.payment_type_id == CARD_PAYMENT_TYPE and order.payment_id:
                try:
                    # check payment status
                    status = alfa_bank.check_extended_status(order.payment_id)["alfa_response"]
                    info.append(("status check result", status))

                    # if status check was successful:
                    if str(status.get("errorCode", '0')) == '0':
                        # money already deposited -- do not delete
                        if status['orderStatus'] == 2:
                            info.append(("ERROR", "deposited"))
                        # money approved -- reverse
                        elif status['orderStatus'] == 1:
                            reverse_result = alfa_bank.reverse(order.payment_id)
                            info.append(("reverse result", reverse_result))
                            if str(reverse_result.get('errorCode', '0')) == '0':
                                to_delete = True
                        # any other status is OK to delete
                        else:
                            to_delete = True
                except Exception as e:
                    info.append(("exception", repr(e)))
            else:
                to_delete = True
            if to_delete:
                order.key.delete()
                info.append(("deleted", True))
            infos.append(info)

        body = "List of orders:\n\n" + \
               "\n\n".join(
                   "\n".join("%s: %s" % t for t in info)
                   for info in infos
               )
        email.send_error("order", "Orders crashed while creating", body)
