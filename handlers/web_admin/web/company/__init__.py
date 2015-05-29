from methods.auth import company_user_required

__author__ = 'dvpermyakov'

from auth import CompanySignupHandler, LoginHandler, LogoutHandler
from base import CompanyBaseHandler


from menu import AddGroupModifierHandler, AddGroupModifierItemHandler, AddMenuItemHandler, AddSingleModifierHandler,\
    CreateCategoryHandler, DownProductHandler, EditGroupModifierHandler, ModifierList, \
    EditGroupModifierItemHandler, EditMenuItemHandler, EditSingleModifierHandler, ListCategoriesHandler, \
    ListMenuItemsHandler, MainMenuHandler, MenuItemInfoHandler, \
    SelectProductForChoiceHandler, SelectProductForModifierHandler, UpProductHandler, UpCategoryHandler, \
    DownCategoryHandler, NoneHandler
from payment_type import CompanyBaseHandler, PaymentTypesHandler
from promos import PromoListHandler
from stop_lists import MainStopListHandler, StopListsHandler
from venues import AddRestrictionHandler, CreateVenueHandler, EditVenueHandler, EnableVenuesHandler, MapVenuesHandler, \
    VenueListHandler
from report import ClientsReportHandler, MenuItemsReportHandler, OrdersReportHandler, ReportHandler
from barista import ListAdmins, ChangeLoginAdmins, ChangePasswordAdmin, AutoCreateAdmins, SignupHandler
from docs import AboutCompanyHandler, SetAboutCompanyHandler, ListDocsHandler
from payment_type import PaymentTypesHandler
from delivery_types import DeliveryTypesHandler, DeliverySlotListHandler, DeliverySlotAddHandler, ChooseSlotsHandler


class AutomationMainHandler(CompanyBaseHandler):
    @company_user_required
    def get(self):
        self.render('/automation.html')