from webapp2_extras import jinja2
from methods import fastcounter
from handlers import api, web_admin, maintenance, share, handle_500
from handlers.api import admin
from webapp2 import Route, WSGIApplication
from webapp2_extras.routes import PathPrefixRoute
import handlers.web_admin.web.company as company_admin
import handlers.web_admin.web.company.delivery as company_delivery

webapp2_config = {
    "webapp2_extras.sessions": {
        "secret_key": '\xfe\xc1\x1d\xc0+\x10\x11\x9a\x0b\xe6\xeb\xd5e \x85NgZ\xcbL\xee\xb0p~\x08\xd5\xa5\x1bAc\x88/'
                      '\xae\t@\xdc\x08d\xe9\xdb'
    },
    "webapp2_extras.auth": {
        "user_model": "models.User"
    }
}


app = WSGIApplication([

    PathPrefixRoute('/docs', [
        Route('/about.html', api.AboutHandler),
        Route('/licence_agreement.html', api.LicenceHandler),
        Route('/nda.html', api.NdaHandler),
        Route('/payment_rules.html', api.PaymentRulesHandler),
    ]),

    PathPrefixRoute('/mt', [
        Route('/companies', maintenance.CompaniesListHandler),

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
            Route('/unbind', api.UnbindCardHandler),
            Route('/register', api.PaymentRegisterHandler),
            Route('/status', api.PaymentStatusHandler),
            Route('/extended_status', api.PaymentExtendedStatusHandler),
            Route('/payment_binding', api.PaymentBindingHandler),
            Route('/reverse', api.PaymentReverseHandler),
            Route('/payment_types', api.PaymentTypesHandler),
        ]),

        PathPrefixRoute('/promo', [
            Route('/list', api.PromoInfoHandler),
            PathPrefixRoute('/gift', [
                Route('/items', api.GiftListHandler),
            ]),
        ]),

        Route('/register', api.RegistrationHandler),
        Route('/demo_info', api.DemoInfoHandler),
        Route('/venues', api.VenuesHandler),
        Route('/client', api.ClientHandler),
        Route('/menu', api.MenuHandler),
        Route('/modifiers', api.ModifiersHandler),
        Route('/dynamic_info', api.DynamicInfoHandler),
        Route('/order', api.OrderHandler),
        Route('/set_order_success', api.ClientSettingSuccessHandler),
        Route('/add_return_comment', api.AddReturnCommentHandler),
        Route('/order_register', api.RegisterOrderHandler),
        Route('/check_order', api.CheckOrderHandler),
        Route('/status', api.StatusHandler),
        Route('/return', api.ReturnOrderHandler),
        Route('/history', api.HistoryHandler),

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

    PathPrefixRoute('/company', [
        Route('/create', company_admin.CompanySignupHandler),
        Route('/login', company_admin.LoginHandler, 'company_login'),
        Route('/logout', company_admin.LogoutHandler),
        Route('/main', company_admin.AutomationMainHandler, 'company_main'),
        Route('/payment_types', company_admin.PaymentTypesHandler),

        Route('/venues', company_admin.EnableVenuesHandler),
        Route('/venues/map', company_admin.MapVenuesHandler),
        Route('/venues/<venue_id:\d+>', company_admin.EditVenueHandler),
        Route('/venues/create', company_admin.CreateVenueHandler),

        PathPrefixRoute('/delivery', [
            PathPrefixRoute('/orders', [
                Route('/items', company_delivery.OrderItemsHandler),
                Route('/confirm', company_delivery.ConfirmOrderHandler),
                Route('/close', company_delivery.CloseOrderHandler),
                Route('/cancel', company_delivery.CancelOrderHandler),
                Route('/current', company_delivery.DeliveryOrdersHandler),
                Route('/new', company_delivery.NewDeliveryOrdersHandler),
            ]),
        ]),

        PathPrefixRoute('/docs', [
            PathPrefixRoute('/set', [
                Route('/about', company_admin.SetAboutCompanyHandler),
            ]),
            Route('/list', company_admin.ListDocsHandler),
            Route('/about', company_admin.AboutCompanyHandler),
        ]),

        PathPrefixRoute('/menu', [
            Route('/main', company_admin.MainMenuHandler),
            PathPrefixRoute('/category', [
                Route('/add', company_admin.CreateCategoryHandler),
                Route('/list', company_admin.ListCategoriesHandler, 'mt_category_list'),
                Route('/up', company_admin.UpCategoryHandler),
                Route('/down', company_admin.DownCategoryHandler),
            ]),
            PathPrefixRoute('/item', [
                Route('/list', company_admin.ListMenuItemsHandler),
                Route('/info', company_admin.MenuItemInfoHandler),
                Route('/add', company_admin.AddMenuItemHandler),
                Route('/edit', company_admin.EditMenuItemHandler),
                Route('/up', company_admin.UpProductHandler),
                Route('/down', company_admin.DownProductHandler),
            ]),
            Route('/product/modifiers/select', company_admin.SelectProductForModifierHandler),
            PathPrefixRoute('/modifiers', [
                Route('/list', company_admin.ModifierList, 'modifiers_list'),
                Route('/add/single_modifier', company_admin.AddSingleModifierHandler),
                Route('/add/group_modifier', company_admin.AddGroupModifierHandler),
                Route('/add/<group_modifier_id:\d+>/group_modifier_item', company_admin.AddGroupModifierItemHandler),
                Route('/edit/single_modifier', company_admin.EditSingleModifierHandler),
                Route('/edit/group_modifier', company_admin.EditGroupModifierHandler),
                Route('/edit/choice', company_admin.EditGroupModifierItemHandler),
                Route('/choices/select', company_admin.SelectProductForChoiceHandler),
            ]),
            PathPrefixRoute('/venue', [
                Route('/list', company_admin.VenueListHandler, 'venues_list'),
                Route('/add_restrictions', company_admin.AddRestrictionHandler),
            ]),
        ]),

        PathPrefixRoute('/stop_list', [
            Route('/main', company_admin.MainStopListHandler, 'main_stop_list'),
            Route('/list', company_admin.StopListsHandler),
        ]),

        PathPrefixRoute('/promos', [
            Route('/list', company_admin.PromoListHandler),
        ]),

        PathPrefixRoute('/report', [
            Route('/main', company_admin.ReportHandler),
            Route('/clients', company_admin.ClientsReportHandler),
            Route('/menu_items', company_admin.MenuItemsReportHandler),
            Route('/orders', company_admin.OrdersReportHandler),
        ]),

        PathPrefixRoute('/barista', [
            Route('/signup', company_admin.SignupHandler),
            Route('/list', company_admin.ListAdmins, 'barista_main'),
            Route('/create', company_admin.AutoCreateAdmins),
            Route('/<admin_id:\d+>/change_login', company_admin.ChangeLoginAdmins),
            Route('/<admin_id:\d+>/change_password', company_admin.ChangePasswordAdmin),
        ]),
    ]),

    PathPrefixRoute('/admin', [
        Route('/login', web_admin.LoginHandler),
        Route('/logout', web_admin.LogoutHandler),

        Route('/orders', web_admin.OrdersHandler),
        Route('/backs', web_admin.ReturnsHandler),
        Route('/history', web_admin.HistoryHandler),

        Route('/check_time', web_admin.CheckTimeHandler),
        Route('/check_update', web_admin.CheckUpdateHandler),
        Route('/done', web_admin.OrderDoneHandler),
        Route('/return_barista', web_admin.OrderCancelHandler),
        Route('/status_up', web_admin.OrderStatusUpdateHandler)
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
