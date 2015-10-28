from handlers.api.user.admin.auth import LoginHandler, LogoutHandler
from handlers.api.user.admin.ping import PingHandler
from handlers.api.user.admin.config import ConfigHandler
from handlers.api.user.admin.lists import CurrentOrdersHandler, HistoryHandler, ReturnsHandler
from handlers.api.user.admin.updates import UpdatesHandler
from handlers.api.user.admin.changes import CancelOrderHandler, DoneOrderHandler, PostponeOrderHandler, ConfirmOrderHandler, WrongVenueHandler
from handlers.api.user.admin.stop_lists import SetStopListHandler, MenuHandler, DynamicInfoHandler, ModifiersHandler
from handlers.api.user.admin.wallet import WalletDepositHandler, WalletDepositHistoryHandler
from handlers.api.user.admin.client_history import ClientHistoryHandler
from handlers.api.user.admin.revenue import RevenueReportMonthHandler, RevenueReportTodayHandler
from handlers.api.user.admin.delivery_types import DeliveryTypesHandler
from handlers.api.user.admin.courier import CourierListHandler
from handlers.api.user.admin.changes import SendToCourierHandler