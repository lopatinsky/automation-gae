from methods.auth import company_user_required

__author__ = 'dvpermyakov'

from auth import CompanySignupHandler, LoginHandler, LogoutHandler
from base import CompanyBaseHandler


from menu import AddGroupModifierHandler, AddGroupModifierItemHandler, AddMenuItemHandler, AddSingleModifierHandler,\
    CreateCategoryHandler, DownProductHandler, EditGroupModifierHandler, ModifierList, \
    EditGroupModifierItemHandler, EditMenuItemHandler, EditSingleModifierHandler, ListCategoriesHandler, \
    ListMenuItemsHandler, MainMenuHandler, MenuItemInfoHandler, \
    SelectProductForChoiceHandler, SelectProductForModifierHandler, UpProductHandler, UpCategoryHandler, \
    DownCategoryHandler, NoneHandler, SelectDefaultChoiceHandler, UpSingleModifierHandler, DownSingleModifierHandler, \
    DownGroupModifierHandler, UpGroupModifierHandler, UpGroupModifierChoiceHandler, DownGroupModifierChoiceHandler, \
    EditCategoryHandler, DeleteCategoryHandler
from payment_type import CompanyBaseHandler, PaymentTypesHandler
from promos import PromoListHandler, AddPromoHandler, ChangeApiKeysHandler, ChooseMenuItemHandler, \
    AddPromoConditionHandler, AddPromoOutcomeHandler, ListGiftsHandler, AddGiftHandler, EditPromoHandler, \
    UpPromoHandler, DownPromoHandler, AddHappyHoursHandler, PromoConflictsHandler
from stop_lists import MainStopListHandler, StopListsHandler
from venues import AddRestrictionHandler, CreateVenueHandler, EditVenueHandler, EnableVenuesHandler, MapVenuesHandler, \
    VenueListHandler, ChooseDeliveryZonesHandler, EditVenueScheduleHandler, EditVenueTimeBreakHandler, \
    EditVenueHolidayScheduleHandler
from report import ClientsReportHandler, MenuItemsReportHandler, OrdersReportHandler, ReportHandler
from barista import ListAdmins, ChangeLoginAdmins, ChangePasswordAdmin, AutoCreateAdmins, SignupHandler
from docs import AboutCompanyHandler, SetAboutCompanyHandler, LegalListHandler, AddLegalListHandler, EditLegalHandler
from delivery_types import DeliveryTypesHandler, DeliverySlotAddHandler, ChooseSlotsHandler, DeliverySlotListHandler, \
    DeliverySlotEditHandler, DeliverySlotSetupTimeHandler
from notifications import ListNewsHandler, AddNewsHandler, PushesListHandler, AddPushesHandler, ChangeParseApiKeys, \
    CancelPushHandler, CancelNewsHandler
from delivery_zones import ListDeliveryZonesHandler, EditDeliveryZoneHandler, MapDeliveryZoneHandler, \
    AddDeliveryZoneHandler, AddingMapDeliveryZoneHandler, UpDeliveryZoneHandler, DownDeliveryZoneHandler, \
    AddingJSFileDeliveryZoneHandler
from promo_code import ListPromoCodeHandler, AddPromoCodeHandler, ActivationsPromoCodeHandler
from alfa_settings import AlfaSettingsHandler
from choose_ns import ChooseNamespaceHandler
from users import ListUsersHandler, EditUsersHandler, CreateUsersHandler


class AutomationMainHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/automation.html')