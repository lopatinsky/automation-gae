from base import CompanyBaseHandler
from methods.auth import company_user_required
from models import DELIVERY_TYPES, DELIVERY_MAP, STATUS_AVAILABLE, STATUS_UNAVAILABLE, Venue, DeliveryType

__author__ = 'dvpermyakov'


class DeliveryTypesHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        def delivery_dict(delivery):
            return {
                'id': delivery.delivery_type,
                'name': DELIVERY_MAP[delivery.delivery_type],
                'value': delivery.status,
                'min_sum': delivery.min_sum
            }

        venues = Venue.query().fetch()
        for venue in venues:
            deliveries = {}
            for delivery in venue.delivery_types:
                deliveries[delivery.delivery_type] = delivery_dict(delivery)
            for delivery_type in DELIVERY_TYPES:
                if delivery_type not in deliveries:
                    delivery = DeliveryType.create(delivery_type)
                    venue.delivery_types.append(delivery)
                    deliveries[delivery.delivery_type] = delivery_dict(delivery)
                    venue.put()
            venue.deliveries = deliveries.values()
        self.render('/delivery_types.html', venues=venues)

    @company_user_required
    def post(self):
        for venue in Venue.query().fetch():
            for delivery in venue.delivery_types:
                confirmed = bool(self.request.get(str('type_%s_%s' % (venue.key.id(), delivery.delivery_type))))
                if bool(delivery.status) != confirmed:
                    if confirmed:
                        delivery.status = STATUS_AVAILABLE
                    else:
                        delivery.status = STATUS_UNAVAILABLE
                delivery.min_sum = self.request.get_range('min_sum_%s_%s' % (venue.key.id(), delivery.delivery_type))
            venue.put()
        self.redirect('/company/main')