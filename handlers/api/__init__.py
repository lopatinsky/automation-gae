__author__ = 'ilyazorin'

from alfa import PaymentBindingHandler, PaymentRegisterHandler, \
    PaymentReverseHandler, PaymentStatusHandler, UnbindCardHandler, \
    PaymentExtendedStatusHandler
from venues import VenuesHandler
from payment_types import PaymentTypesHandler
from menu import MenuHandler, DynamicInfoHandler, ModifiersHandler
from registration import RegistrationHandler
from order import OrderHandler, RegisterOrderHandler, ReturnOrderHandler, CheckOrderHandler, \
    AddReturnCommentHandler
from promo_info import PromoInfoHandler, GiftListHandler, NewsHandler, SharedGiftListHandler
from client import ClientHandler
from history import HistoryHandler, SharedGiftHistoryHandler, SharedInvitationHistoryHandler
from wallet import DepositToWalletHandler, WalletBalanceHandler
from shared import GetInvitationUrlHandler, GetGiftUrlHandler, GiftInfoHandler, GetShareUrlHandler
from twilio import ReceiveSms
from paypal import BindPaypalHandler, UnbindPaypalHandler
from docs import AboutHandler, LicenceHandler, NdaHandler, PaymentRulesHandler
from company import CompanyInfoHandler, CompanyBaseUrlsHandler
from address import AddressByAddressHandler, ValidateAddressHandler
from statuses import StatusHandler, ClientSettingSuccessHandler
