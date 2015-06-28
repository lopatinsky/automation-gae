# coding=utf-8
from base import CompanyBaseHandler
from methods.auth import company_user_required
from models import STATUS_AVAILABLE, STATUS_UNAVAILABLE, Venue, DAY_SECONDS, HOUR_SECONDS, DeliverySlot
from models.venue import DELIVERY_MAP, DELIVERY_TYPES, SELF, IN_CAFE, DELIVERY, PICKUP, DeliveryType

__author__ = 'dvpermyakov'


class DeliveryTypesHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        def delivery_dict(delivery):
            return {
                'id': delivery.delivery_type,
                'name': DELIVERY_MAP[delivery.delivery_type],
                'value': delivery.status,
                'min_time': delivery.min_time,
                'max_time': delivery.max_time
            }

        venues = Venue.query().fetch()
        for venue in venues:
            deliveries = {}
            for delivery in venue.delivery_types:
                deliveries[delivery.delivery_type] = delivery_dict(delivery)
            for delivery_type in DELIVERY_TYPES:
                if delivery_type not in deliveries:
                    delivery = DeliveryType.create(delivery_type)
                    if delivery.delivery_type in [SELF, IN_CAFE]:
                        delivery.max_time = DAY_SECONDS + HOUR_SECONDS  # need hour to order on tomorrow
                    if delivery.delivery_type in [DELIVERY, PICKUP]:
                        delivery.min_time = HOUR_SECONDS
                    venue.delivery_types.append(delivery)
                    deliveries[delivery.delivery_type] = delivery_dict(delivery)
            venue.put()
            venue.deliveries = deliveries.values()
        self.render('/delivery_settings/delivery_types.html', venues=venues)

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
                min_time = self.request.get('min_time_%s_%s' % (venue.key.id(), delivery.delivery_type))
                if min_time:
                    delivery.min_time = int(min_time)
                max_time = self.request.get('max_time_%s_%s' % (venue.key.id(), delivery.delivery_type))
                if max_time:
                    delivery.max_time = int(max_time)
            venue.put()
        self.redirect('/company/main')


class DeliverySlotListHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        slots = DeliverySlot.query().order(DeliverySlot.value).fetch()
        if not slots:
            DeliverySlot(name=u'Сейчас', slot_type=0, value=0).put()
            DeliverySlot(name=u'Через 5 минут', slot_type=0, value=5).put()
            DeliverySlot(name=u'Через 10 минут', slot_type=0, value=10).put()
            DeliverySlot(name=u'Через 15 минут', slot_type=0, value=15).put()
            DeliverySlot(name=u'Через 20 минут', slot_type=0, value=20).put()
            DeliverySlot(name=u'Через 25 минут', slot_type=0, value=25).put()
            DeliverySlot(name=u'Через 30 минут', slot_type=0, value=30).put()
            slots = DeliverySlot.query().order(DeliverySlot.value).fetch()
        for slot in slots:
            slot.slot_type_str = DeliverySlot.CHOICES_MAP[slot.slot_type]
        self.render('/delivery_settings/delivery_slot_list.html', slots=slots)


class DeliverySlotAddHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        types = []
        for type in DeliverySlot.CHOICES:
            types.append({
                'name': DeliverySlot.CHOICES_MAP[type],
                'value': type
            })
        self.render('/delivery_settings/delivery_slot_add.html', types=types)

    @company_user_required
    def post(self):
        slot = DeliverySlot()
        slot.name = self.request.get('name')
        slot.slot_type = self.request.get_range('type')
        value = self.request.get('value')
        if value:
            slot.value = int(value)
        slot.put()
        self.redirect('/company/delivery/slots/list')


class DeliverySlotEditHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        slot_id = self.request.get_range('slot_id')
        slot = DeliverySlot.get_by_id(slot_id)
        if not slot:
            self.abort(400)
        types = []
        for type in DeliverySlot.CHOICES:
            types.append({
                'name': DeliverySlot.CHOICES_MAP[type],
                'value': type
            })
        self.render('/delivery_settings/delivery_slot_add.html', types=types, slot=slot)

    @company_user_required
    def post(self):
        slot_id = self.request.get_range('slot_id')
        slot = DeliverySlot.get_by_id(slot_id)
        if not slot:
            self.abort(400)
        slot.name = self.request.get('name')
        slot.slot_type = self.request.get_range('type')
        value = self.request.get('value')
        if value:
            slot.value = int(value)
        slot.put()
        self.redirect('/company/delivery/slots/list')


class ChooseSlotsHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        venue_id = int(self.request.get('venue_id'))
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        delivery_type = int(self.request.get('delivery_type'))
        delivery_type = venue.get_delivery_type(delivery_type)
        self.render('/delivery_settings/choose_delivery_slots.html', **{
            'venue': venue,
            'delivery_type': delivery_type,
            'slots': DeliverySlot.query().order(DeliverySlot.value).fetch()
        })

    @company_user_required
    def post(self):
        venue_id = int(self.request.get('venue_id'))
        venue = Venue.get_by_id(venue_id)
        if not venue:
            self.abort(400)
        delivery_type = int(self.request.get('delivery_type'))
        delivery_type = venue.get_delivery_type(delivery_type)

        selected_slots = []
        for slot in DeliverySlot.query().fetch():
            confirmed = bool(self.request.get(str(slot.key.id())))
            if confirmed:
                selected_slots.append(slot.key)
        delivery_type.delivery_slots = selected_slots
        venue.put()

        self.redirect('/company/delivery/types')