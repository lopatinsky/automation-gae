# coding=utf-8
import json
import random
import datetime
from google.appengine.api import namespace_manager, mail
from google.appengine.ext import ndb, deferred
from webapp2 import RequestHandler, cached_property
from webapp2_extras import jinja2
from config import Config
from methods import sms_pilot, email_mandrill
from models import DeliverySlot, MenuCategory, MenuItem, CompanyUser, Venue, DAY_SECONDS, HOUR_SECONDS, STATUS_AVAILABLE
from models.payment_types import PaymentType, CASH_PAYMENT_TYPE
from models.schedule import Schedule, DaySchedule
from models.venue import DeliveryType, SELF, IN_CAFE


def _notify_sms(phone, login, password):
    sms_pilot.send_sms(
        [phone],
        u"Логин для входа в демо-приложение: %s, пароль %s. Скачать: http://rbcn.mobi/get/dem?m=sms" % (login, password))


def _notify_email(email, phone, name, login, password):
    email_mandrill.send_email("noreply@ru-beacon.ru", email, "Ваши данные для входа в демо-приложение Ru-beacon",
                              u"""Ваш логин: <b>%s</b><br/>
Ваш пароль: <b>%s</b><br/>
<a href="http://rbcn.mobi/get/dem?m=email">Скачать демо-приложение</a>""" % (login, password))
    mail.send_mail_to_admins(
        "wizard@automation-demo.appspotmail.com",
        u"Создана компания через wizard",
        u"Название: %s\nТелефон: %s\nEmail: %s\nЛогин: %s\nПароль: %s" % (name, phone, email, login, password))


class BaseHandler(RequestHandler):
    @cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template_name, **values):
        rendered = self.jinja2.render_template(template_name, **values)
        self.response.write(rendered)

    def render_json(self, dct):
        self.response.content_type = "application/json"
        self.response.write(json.dumps(dct, separators=(',', ':')))


class WizardWebHandler(BaseHandler):
    def get(self):
        self.render('/wizard/index.html')


class WizardCreateCompanyHandler(BaseHandler):
    _TRANSLIT_DICT = {
        u'а': 'a', u'б': 'b', u'в': 'v', u'г': 'g', u'д': 'd', u'е': 'e',
        u'ё': 'e', u'ж': 'zh', u'з': 'z', u'и': 'i', u'й': 'y', u'к': 'k',
        u'л': 'l', u'м': 'm', u'н': 'n', u'о': 'o', u'п': 'p', u'р': 'r',
        u'с': 's', u'т': 't', u'у': 'u', u'ф': 'f', u'х': 'kh', u'ц': 'ts',
        u'ч': 'ch', u'ш': 'sh', u'щ': 'shch', u'ъ': '', u'ы': 'y', u'ь': '',
        u'э': 'e', u'ю': 'yu', u'я': 'ya'
    }

    @classmethod
    def _find_namespace(cls, name):
        lower_name = name.lower()
        latin_name = ''.join(cls._TRANSLIT_DICT.get(c, c) for c in lower_name)
        clean_name = ''.join(c for c in latin_name if 'a' <= c <= 'z')

        namespace = clean_name
        namespace_manager.set_namespace(namespace)
        cfg = Config.get()
        i = 1
        while cfg:
            namespace = clean_name + str(i)
            namespace_manager.set_namespace(namespace)
            cfg = Config.get()
            i += 1
        namespace_manager.set_namespace(None)
        return namespace

    def post(self):
        data = json.loads(self.request.body)
        name, phone, email = map(data['info'].get, ('name', 'phone', 'email'))
        phone = '7' + ''.join(c for c in phone if '0' <= c <= '9')

        namespace = self._find_namespace(name)
        password = "%04d" % random.randint(0, 10000)
        CompanyUser.create_user(namespace, namespace=namespace, password_raw=password, login=namespace)

        namespace_manager.set_namespace(namespace)
        cfg = Config(id=1)
        cfg.APP_NAME = name
        cfg.DELIVERY_PHONES = [phone]
        cfg.DELIVERY_EMAILS = ['beacon-team@googlegroups.com', email]
        cfg.SUPPORT_EMAILS = [email]
        cfg.ACTION_COLOR = "FF25B8CD"
        cfg.put()

        delivery_slot_keys = [
            DeliverySlot(name=u'Сейчас', slot_type=0, value=0).put(),
            DeliverySlot(name=u'Через 5 минут', slot_type=0, value=5).put(),
            DeliverySlot(name=u'Через 10 минут', slot_type=0, value=10).put(),
            DeliverySlot(name=u'Через 15 минут', slot_type=0, value=15).put(),
            DeliverySlot(name=u'Через 20 минут', slot_type=0, value=20).put(),
            DeliverySlot(name=u'Через 25 минут', slot_type=0, value=25).put(),
            DeliverySlot(name=u'Через 30 минут', slot_type=0, value=30).put()]

        menu = data['menu']
        for i, category_dict in enumerate(menu):
            MenuCategory.generate_category_sequence_number()  # only to increase counter
            category = MenuCategory(title=category_dict["title"], sequence_number=i)
            for j, item in enumerate(category_dict["items"]):
                item = MenuItem(
                    title=item["title"],
                    description=item["description"],
                    picture=item["imageUrl"],
                    price=int(round(item["price"] * 100)),
                    sequence_number=j)
                item_key = item.put()
                category.menu_items.append(item_key)
            category.put()
            for _ in category.menu_items:
                category.generate_sequence_number()  # only to increase counter

        venue_dict = data['venue']
        venue = Venue(
            title=venue_dict['title'],
            description=venue_dict['address'],
            coordinates=ndb.GeoPt(venue_dict['lat'], venue_dict['lng']),
            active=True)
        venue.update_address()
        venue.schedule = Schedule(
            days=[DaySchedule(weekday=i, start=datetime.time(0, 0), end=datetime.time(0, 0)) for i in xrange(1, 8)])

        for delivery_type in (SELF, IN_CAFE):
            delivery = DeliveryType.create(delivery_type)
            delivery.put()
            delivery.status = STATUS_AVAILABLE
            delivery.max_time = DAY_SECONDS + HOUR_SECONDS  # need hour to order on tomorrow
            delivery.delivery_slots = delivery_slot_keys
            venue.delivery_types.append(delivery)

        venue.put()

        PaymentType(id=str(CASH_PAYMENT_TYPE), title="cash", status=STATUS_AVAILABLE).put()

        deferred.defer(_notify_sms, phone, namespace, password)
        deferred.defer(_notify_email, email, phone, name, namespace, password)

        self.render_json({
            'login': namespace,
            'password': password
        })
