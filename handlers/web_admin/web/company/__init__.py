__author__ = 'dvpermyakov'

from auth import SignupHandler, LoginHandler, LogoutHandler
from base import CompanyBaseHandler
from payment_type import PaymentTypesHandler


from menu import AddGroupModifierHandler, AddGroupModifierItemHandler, AddMenuItemHandler, AddSingleModifierHandler,\
    CreateCategoryHandler, DownProductHandler, EditGroupModifierHandler, ModifierList, \
    EditGroupModifierItemHandler, EditMenuItemHandler, EditSingleModifierHandler, ListCategoriesHandler, \
    ListMenuItemsHandler, MainMenuHandler, MenuItemInfoHandler, ModifiersForProductHandler, RemoveMenuItemHandler, \
    SelectProductForChoiceHandler, SelectProductForModifierHandler, UpProductHandler
from payment_type import CompanyBaseHandler, PaymentTypesHandler
from promos import PromoListHandler
from stop_lists import MainStopListHandler, StopListsHandler
from venues import AddRestrictionHandler, CreateVenueHandler, EditVenueHandler, EnableVenuesHandler, MapVenuesHandler, \
    VenueListHandler


class AutomationMainHandler(CompanyBaseHandler):
    def get(self):
        self.render('/automation.html')