from webapp2_extras import jinja2
from config import config
from methods import fastcounter
from handlers import api, web_admin, maintenance, share, handle_500
import handlers.web_admin.web.padmin as padmin
from handlers.api import admin
from webapp2 import Route, WSGIApplication
from webapp2_extras.routes import PathPrefixRoute

webapp2_config = {
    "webapp2_extras.sessions": {
        "secret_key": '\xfe\xc1\x1d\xc0+\x10\x11\x9a\x0b\xe6\xeb\xd5e \x85NgZ\xcbL\xee\xb0p~\x08\xd5\xa5\x1bAc\x88/'
                      '\xae\t@\xdc\x08d\xe9\xdb'
    },
    "webapp2_extras.auth": {
        "user_model": "models.Admin"
    }
}


app = WSGIApplication([

    PathPrefixRoute('/mt', [
        Route('/companies', maintenance.CompaniesListHandler),
        Route('/create_company', maintenance.CreateCompanyHandler),
        Route('/automation', maintenance.AutomationMainHandler),

        Route('/venues', maintenance.EnableVenuesHandler),
        Route('/venues/map', maintenance.MapVenuesHandler),
        Route('/venues/<venue_id:\d+>', maintenance.EditVenueHandler),
        Route('/venues/create', maintenance.CreateVenueHandler),

        Route('/payment_types', maintenance.PaymentTypesHandler),

        Route('/admins', maintenance.AdminsHandler),
        Route('/report', maintenance.ReportHandler),
        PathPrefixRoute('/report', [
            Route('/clients', maintenance.ClientsReportHandler),
            Route('/menu_items', maintenance.MenuItemsReportHandler),
            Route('/tablet_requests_graph', maintenance.TabletRequestGraphHandler),
            Route('/tablet_requests_info', maintenance.TabletInfoHandler),
            Route('/venues', maintenance.VenuesReportHandler),
            Route('/venues_with_dates', maintenance.VenuesReportWithDatesHandler),
            Route('/orders', maintenance.OrdersReportHandler),
            Route('/repeated_orders', maintenance.RepeatedOrdersHandler),
            Route('/square_table', maintenance.SquareTableHandler),
            Route('/notification', maintenance.NotificationsReportHandler),
            Route('/card_binding', maintenance.CardBindingReportHandler),
        ]),

        PathPrefixRoute('/private_office', [
            Route('/list', maintenance.ListPAdmins, 'padmin_main'),
            Route('/create', maintenance.AutoCreatePAdmins),
            Route('/<admin_id:\d+>/change_login', maintenance.ChangeLoginPAdmins),
            Route('/<admin_id:\d+>/change_password', maintenance.ChangePasswordPAdmin),
        ]),

        PathPrefixRoute('/menu', [
            Route('/main', maintenance.MainMenuHandler),
            Route('/category/add', maintenance.CreateCategoryHandler),
            Route('/category/list', maintenance.ListCategoriesHandler, 'mt_category_list'),
            PathPrefixRoute('/item', [
                Route('/list', maintenance.ListMenuItemsHandler),
                Route('/info', maintenance.MenuItemInfoHandler),
                Route('/add', maintenance.AddMenuItemHandler),
                Route('/edit', maintenance.EditMenuItemHandler),
                Route('/delete', maintenance.RemoveMenuItemHandler),
                Route('/up', maintenance.UpProductHandler),
                Route('/down', maintenance.DownProductHandler),
            ]),
            Route('/product/modifiers/list', maintenance.ModifiersForProductHandler),
            Route('/product/modifiers/select', maintenance.SelectProductForModifierHandler),
            PathPrefixRoute('/modifiers', [
                Route('/list', maintenance.ModifierList, 'modifiers_list'),
                Route('/add/single_modifier', maintenance.AddSingleModifierHandler),
                Route('/add/group_modifier', maintenance.AddGroupModifierHandler),
                Route('/add/<group_modifier_id:\d+>/group_modifier_item', maintenance.AddGroupModifierItemHandler),
                Route('/edit/single_modifier', maintenance.EditSingleModifierHandler),
                Route('/edit/group_modifier', maintenance.EditGroupModifierHandler),
                Route('/edit/choice', maintenance.EditGroupModifierItemHandler),
                Route('/choices/select', maintenance.SelectProductForChoiceHandler),
            ]),
            PathPrefixRoute('/venue', [
                Route('/list', maintenance.VenueListHandler, 'venues_list'),
                Route('/add_restrictions', maintenance.AddRestrictionHandler),
            ]),
        ]),

        PathPrefixRoute('/stop_list', [
            Route('/main', maintenance.MainStopListHandler, 'main_stop_list'),
            Route('/list', maintenance.StopListsHandler),
        ]),

        PathPrefixRoute('/promos', [
            Route('/list', maintenance.PromoListHandler),
        ]),

        Route('/check_menu', maintenance.CheckMenuHandler),
        Route('/name_confirmation', maintenance.NameConfirmationHandler),
    ]),

    PathPrefixRoute('/api', [
        PathPrefixRoute('/admin', [
            Route('/login', admin.LoginHandler),
            Route('/logout', admin.LogoutHandler),
            Route('/ping', admin.PingHandler),

            Route('/orders/current', admin.CurrentOrdersHandler),
            Route('/orders/updates', admin.UpdatesHandler),

            Route('/orders/returns', admin.ReturnsHandler),
            Route('/orders/history', admin.HistoryHandler),

            Route('/orders/<order_id:\d+>/cancel', admin.CancelOrderHandler),
            Route('/orders/<order_id:\d+>/close', admin.DoneOrderHandler),
            Route('/orders/<order_id:\d+>/postpone', admin.PostponeOrderHandler),

            Route('/menu', admin.MenuHandler),
            Route('/modifiers', admin.ModifiersHandler),
            Route('/dynamic_info', admin.DynamicInfoHandler),
            Route('/stop_list/set', admin.SetStopListHandler),
            Route('/wallet/deposit', admin.WalletDepositHandler),
            Route('/wallet/deposit_history', admin.WalletDepositHistoryHandler),

            Route('/clients/<client_id:\d+>/history', admin.ClientHistoryHandler),
            
            Route('/revenue/today', admin.RevenueReportTodayHandler),
            Route('/revenue/month', admin.RevenueReportMonthHandler),
        ]),

        PathPrefixRoute('/payment', [
            Route('/unbind.php', api.UnbindCardHandler),
            Route('/register.php', api.PaymentRegisterHandler),
            Route('/status.php', api.PaymentStatusHandler),
            Route('/extended_status', api.PaymentExtendedStatusHandler),
            Route('/payment_binding.php', api.PaymentBindingHandler),
            Route('/reverse.php', api.PaymentReverseHandler),
            Route('/payment_types.php', api.PaymentTypesHandler),
        ]),

        Route('/register', api.RegistrationHandler),
        Route('/demo_info', api.DemoInfoHandler),
        Route('/venues.php', api.VenuesHandler),
        Route('/client.php', api.ClientHandler),
        Route('/menu.php', api.MenuHandler),
        Route('/modifiers', api.ModifiersHandler),
        Route('/dynamic_info', api.DynamicInfoHandler),
        Route('/order.php', api.OrderHandler),
        Route('/set_order_success', api.ClientSettingSuccessHandler),
        Route('/add_return_comment', api.AddReturnCommentHandler),
        Route('/order_register.php', api.RegisterOrderHandler),
        Route('/check_order', api.CheckOrderHandler),
        Route('/status.php', api.StatusHandler),
        Route('/return.php', api.ReturnOrderHandler),
        Route('/history', api.HistoryHandler),

        Route('/promos', api.PromoInfoHandler),

        Route('/wallet/balance', api.WalletBalanceHandler),
        Route('/wallet/deposit', api.DepositToWalletHandler),

        Route('/update/promo', api.UpdateOrderPromos),
        PathPrefixRoute('/shared', [
            Route('/info', api.GetSharedInfo),
            PathPrefixRoute('/invitation', [
                Route('/get_url', api.GetInvitationUrlHandler),
            ]),
            PathPrefixRoute('/gift', [
                Route('/get_url', api.GetGiftUrlHandler),
                Route('/text', api.GetPreText),
            ]),
        ]),
    ]),

    PathPrefixRoute('/admin', [

        PathPrefixRoute('/private_office', [
            PathPrefixRoute('/report', [
                Route('', padmin.ReportHandler, 'padmin_report'),
                Route('/clients', padmin.ClientsReportHandler),
                Route('/menu_items', padmin.MenuItemsReportHandler),
                Route('/orders', padmin.OrdersReportHandler),
            ]),
            Route('/login', padmin.LoginHandler, 'padmin_login'),
            Route('/logout', padmin.LogoutHandler),
        ]),

        Route('/login', web_admin.LoginHandler),
        Route('/signup', web_admin.SignupHandler),
        Route('/logout', web_admin.LogoutHandler),

        Route('/orders.php', web_admin.OrdersHandler),
        Route('/backs.php', web_admin.ReturnsHandler),
        Route('/history.php', web_admin.HistoryHandler),

        Route('/check_time.php', web_admin.CheckTimeHandler),
        Route('/check_update.php', web_admin.CheckUpdateHandler),
        Route('/done.php', web_admin.OrderDoneHandler),
        Route('/return_barista.php', web_admin.OrderCancelHandler),
        Route('/status_up.php', web_admin.OrderStatusUpdateHandler)
    ]),

    Route('/task/counter_persist_incr', fastcounter.CounterPersistIncr),
    Route('/task/check_order_success', api.CheckOrderSuccessHandler),

    Route('/twilio/sms/get', api.ReceiveSms),

    Route('/get/<t:[abcd]?><platform:[ia]>', share.GATrackDownloadHandler),
    Route('/get/<t:[abcd]?><platform:[ia]>/<client_id:\d+>', share.GATrackDownloadHandler),

    Route('/get/splash', share.GATrackSplashHandler),
    Route('/get/splash/<button:[ia]>', share.GATrackSplashHandler),
], config=webapp2_config)

jinja2.set_jinja2(jinja2.Jinja2(app), app=app)

app.error_handlers[500] = handle_500
