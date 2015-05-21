__author__ = 'ilyazorin'

from alfa import PaymentBindingHandler, PaymentRegisterHandler, \
    PaymentReverseHandler, PaymentStatusHandler, UnbindCardHandler, \
    PaymentExtendedStatusHandler
from venues import VenuesHandler
from payment_types import PaymentTypesHandler
from menu import MenuHandler, DynamicInfoHandler, ModifiersHandler
from registration import RegistrationHandler
from order import OrderHandler, RegisterOrderHandler, StatusHandler, ReturnOrderHandler, CheckOrderHandler, \
    AddReturnCommentHandler
from promo_info import DemoInfoHandler, PromoInfoHandler, GiftListHandler
from client import ClientHandler
from history import HistoryHandler
from response_order_status import CheckOrderSuccessHandler, ClientSettingSuccessHandler
from wallet import DepositToWalletHandler, WalletBalanceHandler
from update_order import UpdateOrderPromos
from shared import GetSharedInfo, GetInvitationUrlHandler, GetGiftUrlHandler, GetPreText
from twilio import ReceiveSms
from paypal import BindPaypalHandler, UnbindPaypalHandler
from docs import AboutHandler, LicenceHandler, NdaHandler, PaymentRulesHandler
from company import CompanyInfoHandler
from address import AddressByAddressHandler
