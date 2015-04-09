import datetime
from .base import BaseHandler
from methods.orders.validation import validate_order
from models import Venue, MenuItem, STATUS_AVAILABLE, Client


class CheckMenuHandler(BaseHandler):
    @staticmethod
    def check(client, order_items, venues, hour):
        datetime_to_check = datetime.datetime.combine(datetime.date.today(), datetime.time(hour, 0))
        delivery_time = int((datetime_to_check - datetime.datetime.now()).total_seconds() / 60)

        data = {}

        for venue in venues:
            venue_data = {}
            validation_details = validate_order(client, order_items, None, venue, delivery_time,
                                                with_details=True)['details']
            for details_item in validation_details:
                venue_data[details_item.item.id()] = details_item.price if not details_item.errors else None
            data[venue.key.id()] = venue_data

        return data

    def get(self):
        self.abort(501)  # this endpoint does not work!
        venue_ids = [
            1,  # mil
            4801814507552768,  # ftower
            5656058538229760,  # gstolic
            5660980839186432,  # dmitr
            5786976926040064,  # tvyamsk
            6209189391106048,  # ilikewine

            5682617542246400,  # noev

            5093108584808448,  # omega

            6110169389858816,  # setun
            6490664367816704,  # monarch
            4851681627996160,  # lefort

            5083289484263424,  # million
            4661077019197440,  # tkachi
            5313962648272896,  # kronv

            5547219436437504,  # etazhi

            5364764460974080,  # krivok

            5224026972618752,  # alkon
        ]
        venues = [Venue.get_by_id(vid) for vid in venue_ids]
        items = MenuItem.query(MenuItem.status == STATUS_AVAILABLE).fetch()
        items = sorted(items, key=lambda i: (i.price, i.title))

        order_items = [{"id": item.key.id(), "quantity": 1} for item in items]
        client = Client.get_by_id(1)
        
        data = self.check(client, order_items, venues, 13)
        hh_data = self.check(client, order_items, venues, 8)

        self.render('check_menu.html', prices=data, hh_prices=hh_data, items=items, venues=venues)
