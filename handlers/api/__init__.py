__author__ = 'ilyazorin'

from alfa import PaymentRegisterHandler, \
    PaymentReverseHandler, PaymentStatusHandler, UnbindCardHandler, \
    PaymentExtendedStatusHandler
from venues import VenuesHandler
from payment_types import PaymentTypesHandler
from menu import MenuHandler, DynamicInfoHandler, ModifiersHandler, CategoryHandler
from registration import RegistrationHandler
from order import OrderHandler, RegisterOrderHandler, ReturnOrderHandler, CheckOrderHandler, OrderReviewHandler
from promo_info import PromoInfoHandler, GiftListHandler, NewsHandler, SharedGiftListHandler
from client import ClientHandler
from history import HistoryHandler, SharedGiftHistoryHandler, SharedInvitationHistoryHandler
from wallet import DepositToWalletHandler, WalletBalanceHandler
from shared import GetInvitationUrlHandler, GetGiftUrlHandler, GetInvitationInfoHandler
from twilio import ReceiveSms
from paypal import BindPaypalHandler, UnbindPaypalHandler
from docs import AboutHandler, LicenceHandler, NdaHandler, PaymentRulesHandler, PaypalPrivacyPolicyHandler, \
    PaypalUserAgreementHandler
from company import CompanyInfoHandler, CompanyBaseUrlsHandler, CompanyModulesHandler
from address import AddressByAddressHandler, ValidateAddressHandler
from statuses import StatusHandler, ClientSettingSuccessHandler
from demo import DemoLoginHandler
from promo_code import EnterPromoCode, PromoCodeHistoryHandler
from subscription import BuySubscriptionHandler, SubscriptionInfoHandler, SubscriptionTariffsHandler
from geo_push import AddPushHandler
