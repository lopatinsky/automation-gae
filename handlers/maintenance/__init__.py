from admins import AdminsHandler
from report import ReportHandler, ClientsReportHandler, MenuItemsReportHandler, VenuesReportHandler, \
    VenuesReportWithDatesHandler, OrdersReportHandler, RepeatedOrdersHandler, SquareTableHandler,\
    NotificationsReportHandler, CardBindingReportHandler
from tablet_requests_report import TabletRequestGraphHandler, TabletInfoHandler
from name_confirmed import NameConfirmationHandler
from private_office import ListPAdmins, ChangeLoginPAdmins, ChangePasswordPAdmin, AutoCreatePAdmins
from menu import ListCategoriesHandler, ListMenuItemsHandler, MenuItemInfoHandler, AddMenuItemHandler, \
    CreateCategoryHandler, MainMenuHandler, SelectProductForModifierHandler, ModifiersForProductHandler, ModifierList, \
    AddSingleModifierHandler, AddGroupModifierHandler, AddGroupModifierItemHandler, EditMenuItemHandler, \
    RemoveMenuItemHandler, SelectProductForChoiceHandler
from check_menu import CheckMenuHandler
from venues import VenueListHandler, AddRestrictionHandler, EditVenueHandler, EnableVenuesHandler, CreateVenueHandler
from stop_lists import MainStopListHandler, StopListsHandler
from payment_type import PaymentTypesHandler
from automation import AutomationMainHandler