from enable_venues import EnableVenuesHandler
from edit_venue import EditVenueHandler
from admins import AdminsHandler
from report import ReportHandler, ClientsReportHandler, MenuItemsReportHandler, VenuesReportHandler, \
    VenuesReportWithDatesHandler, OrdersReportHandler, RepeatedOrdersHandler, SquareTableHandler,\
    NotificationsReportHandler, CardBindingReportHandler
from tablet_requests_report import TabletRequestGraphHandler, TabletInfoHandler
from name_confirmed import NameConfirmationHandler
from private_office import ListPAdmins, ChangeLoginPAdmins, ChangePasswordPAdmin, AutoCreatePAdmins
from menu import ListCategoriesHandler, ListMenuItemsHandler, MenuItemInfoHandler, AddMenuItemHandler, CreateCategoryHandler
from check_menu import CheckMenuHandler
