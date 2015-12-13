from webapp2_extras import jinja2
from webapp2 import Route, WSGIApplication
from webapp2_extras.routes import PathPrefixRoute

from handlers.api.user import admin
from handlers import web_app
from handlers import wizard, web_admin, ext_api
from methods import fastcounter
from handlers import api, maintenance, handle_500
import handlers.web_admin.web.company as company_admin
from handlers.web_admin.web.company.config_setup import *
from handlers.api.user import courier
import handlers.web_admin.web.company.delivery as company_delivery
import handlers.web_admin.web.company.excel as company_excel
from handlers.api.proxy import unified_app
from handlers import tasks
from handlers import email_api
from handlers.api import mivako

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
    PathPrefixRoute('/email', [
        PathPrefixRoute('/order', [
            Route('/close', email_api.DoneOrderHandler),
            Route('/cancel', email_api.CancelOrderHandler),
            Route('/postpone', email_api.PostponeOrderHandler),
            Route('/confirm', email_api.ConfirmOrderHandler),
        ]),
    ]),

    PathPrefixRoute('/docs', [
        Route('/about.html', api.AboutHandler),
        Route('/licence_agreement.html', api.LicenceHandler),
        Route('/nda.html', api.NdaHandler),
        Route('/payment_rules.html', api.PaymentRulesHandler),
        Route('/paypal_privacy_policy.html', api.PaypalPrivacyPolicyHandler),
        Route('/paypal_user_agreement.html', api.PaypalUserAgreementHandler),
    ]),

    PathPrefixRoute('/mt', [
        PathPrefixRoute('/splash', [
            Route('/main', maintenance.SplashMainHandler),
            Route('/smart_banner', maintenance.SmartBannerHandler),
            Route('/splash_screen', maintenance.SplashScreenHandler),
        ]),
        Route('/companies', maintenance.CompaniesListHandler),
        Route('/report', maintenance.ReportHandler),
        PathPrefixRoute('/report', [
            Route('/companies', maintenance.CompaniesReportHandler),
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
        Route('/name_confirmation', maintenance.NameConfirmationHandler),
    ]),

    PathPrefixRoute('/api', [
        PathPrefixRoute('/demo', [
            Route('/login', api.DemoLoginHandler),
        ]),

        PathPrefixRoute('/courier', [
            Route('/login', courier.LoginHandler),
            Route('/logout', courier.LogoutHandler),
            Route('/info', courier.InfoHandler),
            PathPrefixRoute('/orders', [
                Route('/current', courier.CurrentOrdersHandler),
                Route('/updates', courier.UpdatesHandler),
                Route('/history', courier.HistoryHandler),
                PathPrefixRoute('/<order_id:\d+>', [
                    Route('/done', courier.DoneOrderHandler),
                ]),
            ]),
        ]),

        PathPrefixRoute('/admin', [
            Route('/login', admin.LoginHandler),
            Route('/logout', admin.LogoutHandler),
            Route('/config', admin.ConfigHandler),
            Route('/ping', admin.PingHandler),
            Route('/delivery_types', admin.DeliveryTypesHandler),

            PathPrefixRoute('/orders', [
                Route('/current', admin.CurrentOrdersHandler),
                Route('/updates', admin.UpdatesHandler),
                Route('/returns', admin.ReturnsHandler),
                Route('/history', admin.HistoryHandler),
                PathPrefixRoute('/<order_id:\d+>', [
                    Route('/cancel', admin.CancelOrderHandler),
                    Route('/close', admin.DoneOrderHandler),
                    Route('/postpone', admin.PostponeOrderHandler),
                    Route('/confirm', admin.ConfirmOrderHandler),
                    Route('/sync', admin.SyncRestoOrderHandler),
                    Route('/send_to_courier', admin.SendToCourierHandler),
                    Route('/wrong_venue', admin.WrongVenueHandler),
                ])
            ]),

            Route('/menu', admin.MenuHandler),
            Route('/modifiers', admin.ModifiersHandler),
            Route('/dynamic_info', admin.DynamicInfoHandler),
            PathPrefixRoute('/stop_list', [
                Route('/set', admin.SetStopListHandler),
            ]),
            PathPrefixRoute('/wallet', [
                Route('/deposit', admin.WalletDepositHandler),
                Route('/deposit_history', admin.WalletDepositHistoryHandler),
            ]),
            Route('/clients/<client_id:\d+>/history', admin.ClientHistoryHandler),
            PathPrefixRoute('/revenue', [
                Route('/today', admin.RevenueReportTodayHandler),
                Route('/month', admin.RevenueReportMonthHandler),
            ]),
            PathPrefixRoute('/courier', [
                Route('/list', admin.CourierListHandler),
            ]),
        ]),

        PathPrefixRoute('/payment', [
            PathPrefixRoute('/paypal', [
                Route('/bind', api.BindPaypalHandler),
                Route('/unbind', api.UnbindPaypalHandler),
            ]),
            Route('/unbind', api.UnbindCardHandler),
            Route('/register', api.PaymentRegisterHandler),
            Route('/status', api.PaymentStatusHandler),
            Route('/extended_status', api.PaymentExtendedStatusHandler),
            Route('/reverse', api.PaymentReverseHandler),
            Route('/payment_types', api.PaymentTypesHandler),
        ]),

        Route('/register', api.RegistrationHandler),
        Route('/client', api.ClientHandler),
        Route('/venues', api.VenuesHandler),
        Route('/menu', api.MenuHandler),
        Route('/category', api.CategoryHandler),
        Route('/modifiers', api.ModifiersHandler),
        Route('/remainders', api.RemainderHandler),
        Route('/dynamic_info', api.DynamicInfoHandler),
        Route('/check_order', api.CheckOrderHandler),
        Route('/order_register', api.RegisterOrderHandler),
        Route('/order', api.OrderHandler),
        Route('/set_order_success', api.ClientSettingSuccessHandler),
        Route('/review', api.OrderReviewHandler),
        Route('/status', api.StatusHandler),
        Route('/return', api.ReturnOrderHandler),
        Route('/history', api.HistoryHandler),
        Route('/news', api.NewsHandler),

        PathPrefixRoute('/proxy', [
            PathPrefixRoute('/unified_app', [
                Route('/companies', unified_app.CompaniesHandler),
                Route('/cities', unified_app.CitiesHandler),  # it can be used for non-proxy companies
                Route('/venues', unified_app.VenuesHandler),
                Route('/menu', unified_app.MenuHandler),
                Route('/product', unified_app.ProductHandler),
            ]),
        ]),

        PathPrefixRoute('/address', [
            Route('/validate', api.ValidateAddressHandler),
            Route('/by_street', api.AddressByAddressHandler),
        ]),

        PathPrefixRoute('/promo', [
            Route('/list', api.PromoInfoHandler),
            PathPrefixRoute('/gift', [
                Route('/items', api.GiftListHandler),
            ]),
        ]),

        PathPrefixRoute('/menu_item_day', [
            Route('/info', api)
        ]),

        PathPrefixRoute('/subscription', [
            Route('/info', api.SubscriptionInfoHandler),
            Route('/tariffs', api.SubscriptionTariffsHandler),
            Route('/buy', api.BuySubscriptionHandler),
        ]),

        PathPrefixRoute('/promo_code', [
            Route('/enter', api.EnterPromoCode),
            Route('/history', api.PromoCodeHistoryHandler),
        ]),

        PathPrefixRoute('/wallet', [
            Route('/balance', api.WalletBalanceHandler),
            Route('/deposit', api.DepositToWalletHandler),
        ]),

        PathPrefixRoute('/company', [
            Route('/info', api.CompanyInfoHandler),
            Route('/modules', api.CompanyModulesHandler),
            Route('/base_urls', api.CompanyBaseUrlsHandler),
        ]),

        PathPrefixRoute('/shared', [
            PathPrefixRoute('/invitation', [
                Route('/info', api.GetInvitationInfoHandler),
                Route('/history', api.SharedInvitationHistoryHandler),
                Route('/get_url', api.GetInvitationUrlHandler),
            ]),
            PathPrefixRoute('/gift', [
                Route('/items', api.SharedGiftListHandler),
                Route('/history', api.SharedGiftHistoryHandler),
                Route('/get_url', api.GetGiftUrlHandler),
                Route('/get_mivako_url', mivako.MivakoGetUrlHandler),
            ]),
        ]),
        PathPrefixRoute('/geo_push', [
            Route('/add', api.AddPushHandler),
        ]),
    ]),

    PathPrefixRoute('/company', [
        Route('/create', company_admin.CompanySignupHandler),
        Route('/login', company_admin.LoginHandler, 'company_login'),
        Route('/logout', company_admin.LogoutHandler, 'company_logout'),
        Route('/main', company_admin.AutomationMainHandler, 'company_main'),
        Route('/choose', company_admin.ChooseNamespaceHandler, 'company_choose_namespace'),
        Route('/payment_types', company_admin.PaymentTypesHandler),

        PathPrefixRoute('/config_settings', [
            Route('', ConfigMainHandler),
            Route('/invitation_module_setup', SetInvitationModuleHandler),
            Route('/create_branch_api_key', CreateBranchApiKeyHandler)
        ]),

        PathPrefixRoute('/venues', [
            Route('', company_admin.EnableVenuesHandler),
            Route('/<venue_id:\d+>', company_admin.EditVenueHandler),
            Route('/map', company_admin.MapVenuesHandler),
            Route('/create', company_admin.CreateVenueHandler),
            Route('/choose_zones', company_admin.ChooseDeliveryZonesHandler),
            Route('/schedule', company_admin.EditVenueScheduleHandler),
            Route('/time_break', company_admin.EditVenueTimeBreakHandler),
        ]),

        PathPrefixRoute('/delivery', [
            Route('/types', company_admin.DeliveryTypesHandler),
            PathPrefixRoute('/zone', [
                Route('/list', company_admin.ListDeliveryZonesHandler),
                Route('/add', company_admin.AddDeliveryZoneHandler),
                Route('/edit', company_admin.EditDeliveryZoneHandler),
                Route('/add_by_map', company_admin.AddingMapDeliveryZoneHandler),
                Route('/map', company_admin.MapDeliveryZoneHandler),
                Route('/up', company_admin.UpDeliveryZoneHandler),
                Route('/down', company_admin.DownDeliveryZoneHandler),
            ]),
            PathPrefixRoute('/orders', [
                Route('/items', company_delivery.OrderItemsHandler),
                Route('/confirm', company_delivery.ConfirmOrderHandler),
                Route('/close', company_delivery.CloseOrderHandler),
                Route('/cancel', company_delivery.CancelOrderHandler),
                Route('/current', company_delivery.DeliveryOrdersHandler),
                Route('/new', company_delivery.NewDeliveryOrdersHandler),
            ]),
            PathPrefixRoute('/slots', [
                Route('/list', company_admin.DeliverySlotListHandler),
                Route('/add', company_admin.DeliverySlotAddHandler),
                Route('/edit', company_admin.DeliverySlotEditHandler),
                Route('/choose', company_admin.ChooseSlotsHandler),
            ]),
        ]),

        PathPrefixRoute('/docs', [
            PathPrefixRoute('/legal', [
                Route('/list', company_admin.LegalListHandler),
                Route('/add', company_admin.AddLegalListHandler),
                Route('/edit', company_admin.EditLegalHandler),
            ]),
            PathPrefixRoute('/set', [
                Route('/about', company_admin.SetAboutCompanyHandler),
            ]),
            Route('/about', company_admin.AboutCompanyHandler),
        ]),

        PathPrefixRoute('/excel', [
            Route('/menu', company_excel.ParseMenuHandler),
        ]),

        PathPrefixRoute('/menu', [
            Route('/main', company_admin.MainMenuHandler),
            PathPrefixRoute('/category', [
                Route('/add', company_admin.CreateCategoryHandler),
                Route('/edit', company_admin.EditCategoryHandler),
                Route('/list', company_admin.ListCategoriesHandler, 'mt_category_list'),
                Route('/up', company_admin.UpCategoryHandler),
                Route('/down', company_admin.DownCategoryHandler),
                Route('/delete', company_admin.DeleteCategoryHandler),
            ]),
            PathPrefixRoute('/item', [
                Route('/list', company_admin.ListMenuItemsHandler),
                Route('/info', company_admin.MenuItemInfoHandler),
                Route('/add', company_admin.AddMenuItemHandler),
                Route('/edit', company_admin.EditMenuItemHandler),
                Route('/up', company_admin.UpProductHandler),
                Route('/down', company_admin.DownProductHandler),
                Route('/None', company_admin.NoneHandler),  # just erase 404 error
            ]),
            Route('/product/modifiers/select', company_admin.SelectProductForModifierHandler),
            PathPrefixRoute('/modifiers', [
                Route('/list', company_admin.ModifierList, 'modifiers_list'),
                PathPrefixRoute('/add', [
                    Route('/single_modifier', company_admin.AddSingleModifierHandler),
                    Route('/group_modifier', company_admin.AddGroupModifierHandler),
                    Route('/<group_modifier_id:\d+>/group_modifier_item', company_admin.AddGroupModifierItemHandler),
                ]),
                PathPrefixRoute('/edit', [
                    Route('/single_modifier', company_admin.EditSingleModifierHandler),
                    Route('/group_modifier', company_admin.EditGroupModifierHandler),
                    Route('/choice', company_admin.EditGroupModifierItemHandler),
                ]),
                PathPrefixRoute('/up', [
                    Route('/single_modifier', company_admin.UpSingleModifierHandler),
                    Route('/group_modifier', company_admin.UpGroupModifierHandler),
                    Route('/group_modifier_choice', company_admin.UpGroupModifierChoiceHandler),
                ]),
                PathPrefixRoute('/down', [
                    Route('/single_modifier', company_admin.DownSingleModifierHandler),
                    Route('/group_modifier', company_admin.DownGroupModifierHandler),
                    Route('/group_modifier_choice', company_admin.DownGroupModifierChoiceHandler),
                ]),
                PathPrefixRoute('/choices', [
                    Route('/select', company_admin.SelectProductForChoiceHandler),
                    Route('/default', company_admin.SelectDefaultChoiceHandler),
                ]),
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
            Route('/conflicts', company_admin.PromoConflictsHandler),
            Route('/up', company_admin.UpPromoHandler),
            Route('/down', company_admin.DownPromoHandler),
            Route('/api_keys', company_admin.ChangeApiKeysHandler),
            Route('/add', company_admin.AddPromoHandler),
            Route('/edit', company_admin.EditPromoHandler),
            Route('/choose', company_admin.ChooseMenuItemHandler),
            PathPrefixRoute('/conditions', [
                Route('/add', company_admin.AddPromoConditionHandler),
                Route('/happy_hours', company_admin.AddHappyHoursHandler),
            ]),
            PathPrefixRoute('/outcomes', [
                Route('/add', company_admin.AddPromoOutcomeHandler),
            ]),
            PathPrefixRoute('/gifts', [
                Route('/list', company_admin.ListGiftsHandler),
                Route('/add', company_admin.AddGiftHandler),
            ]),
        ]),

        PathPrefixRoute('/promo_code', [
            Route('/list', company_admin.ListPromoCodeHandler),
            Route('/activations', company_admin.ActivationsPromoCodeHandler),
            Route('/add', company_admin.AddPromoCodeHandler),
        ]),

        PathPrefixRoute('/notifications', [
            PathPrefixRoute('/news', [
                Route('/list', company_admin.ListNewsHandler),
                Route('/add', company_admin.AddNewsHandler),
                Route('/cancel', company_admin.CancelNewsHandler),
            ]),
            PathPrefixRoute('/pushes', [
                Route('/list', company_admin.PushesListHandler),
                Route('/add', company_admin.AddPushesHandler),
                Route('/cancel', company_admin.CancelPushHandler),
                Route('/api_keys', company_admin.ChangeParseApiKeys),
            ]),
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
            PathPrefixRoute('/<admin_id:\d+>', [
                Route('/change_login', company_admin.ChangeLoginAdmins),
                Route('/change_password', company_admin.ChangePasswordAdmin),
            ]),
        ]),

        PathPrefixRoute('/user', [
            Route('/list', company_admin.ListUsersHandler),
            Route('/create', company_admin.CreateUsersHandler),
            Route('/edit', company_admin.EditUsersHandler),
        ]),

        Route('/alfa_settings', company_admin.AlfaSettingsHandler),
    ]),

    Route('/barista', web_admin.WebBaristaHandler),

    Route('/', web_app.WebAppHandler),

    Route('/wizard', wizard.WizardWebHandler),
    Route('/wizard/api/create', wizard.WizardCreateCompanyHandler),

    PathPrefixRoute('/task', [
        Route('/counter_persist_incr', fastcounter.CounterPersistIncr),
        Route('/check_order_success', tasks.CheckOrderSuccessHandler),
        PathPrefixRoute('/news', [
            Route('/start', tasks.StartNewsHandler),
        ]),
        PathPrefixRoute('/pushes', [
            Route('/start', tasks.StartPushesHandler),
            Route('/review', tasks.SendPushReviewHandler),
        ]),
    ]),

    PathPrefixRoute('/ext', [
        Route('/export_legals', ext_api.ExportLegalsHandler),
    ]),

    Route('/twilio/sms/get', api.ReceiveSms),
], config=webapp2_config)

jinja2.set_jinja2(jinja2.Jinja2(app), app=app)

app.error_handlers[500] = handle_500
