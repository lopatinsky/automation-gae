import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { ClientStore, VenuesStore, AddressStore, PaymentsStore, OrderStore } from './stores';

const base_url = "http://mycompany.app.doubleb-automation-production.appspot.com";

const Actions = {
    INIT: "INIT",
    UPDATE: "UPDATE",
    ERROR: "ERROR",
    CANCEL: "CANCEL",
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    load() {
        this._registerClient();
        this._loadVenues();
        this._loadMenu();
        this._loadPaymentTypes();
        this._loadCompanyInfo();
    },

    setClientInfo(name, phone, email) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: 'client',
                name: name,
                phone: phone,
                email: email
            }
        })
    },

    sendClientInfo() {
        request
            .post(base_url + '/api/client')
            .type('form')
            .send({
                client_id: ClientStore.getClientId(),
                client_name: ClientStore.getName(),
                client_phone: ClientStore.getPhone(),
                client_email: ClientStore.getEmail()
            })
            .end((err, res) => {});
    },

    _loadMenu() {
        request
            .get(base_url + '/api/menu')
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "menu",
                            menu: res.body.menu
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "menu"
                        }
                    })
                }
            });
    },

    _loadVenues() {
        request
            .get(base_url + '/api/venues')
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "venues",
                            venues: res.body.venues
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "venues"
                        }
                    })
                }
            });
    },

    _loadPaymentTypes() {
        request
            .get(base_url + '/api/payment/payment_types')
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "payment_types",
                            payment_types: res.body.payment_types
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "payment_types"
                        }
                    });
                }
            });
    },

    _loadCompanyInfo() {
        request
            .get(base_url + '/api/company/info')
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "address",
                            cities: res.body.cities
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "address"
                        }
                    })
                }
            });
    },

    _registerClient() {
        request
            .post(base_url + '/api/register')
            .query({ client_id: ClientStore.getClientId() })
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "register",
                            client_id: res.body.client_id
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "register"
                        }
                    })
                }
            });
    },

    setMenuItem(item) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "menu_item",
                item: item
            }
        })
    },

    setModifier(modifier) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "modifier",
                modifier: modifier
            }
        })
    },

    checkOrder() {
        request
            .post(base_url + '/api/check_order')
            .type('form')
            .send(OrderStore.getCheckOrderDict())
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.UPDATE,
                        data: {
                            request: "order",
                            total_sum: res.body.total_sum,
                            delivery_sum: res.body.delivery_sum,
                            delivery_sum_str: res.body.delivery_sum_str,
                            promos: res.body.promos,
                            errors: res.body.errors,
                            orderGifts: res.body.new_order_gifts
                        }
                    });
                } else {
                    alert(res.status);
                }
            });
    },

    order() {
        request
            .post(base_url + '/api/order')
            .type('form')
            .send({
                order: JSON.stringify(OrderStore.getOrderDict())
            })
            .end((err, res) => {
                if (res.status == 201) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "order",
                            orderId: res.body.order_id
                        }
                    });
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.ERROR,
                        data: {
                            request: "order",
                            error: res.body.description
                        }
                    });
                }
            });
    },

    cancelOrder(order_id) {
        request
            .post(base_url + '/api/return')
            .type('form')
            .send({
                order_id: order_id
            })
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.CANCEL,
                        data: {
                            request: "order",
                            description: "Ваш заказ был успешно отменен"
                        }
                    });
                } else if (res.status == 412 || res.status == 422) {
                    AppDispatcher.dispatch({
                        actionType: this.CANCEL,
                        data: {
                            request: "order",
                            description: res.body.description
                        }
                    });
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.CANCEL,
                        data: {
                            request: "order",
                            description: "Непредвиденная ошибка"
                        }
                    });
                }
            });
    },

    setOrderSuccess(orderId) {
        request
            .post(base_url + '/api/set_order_success')
            .type('form')
            .send({
                order_id: orderId
            })
            .end((err, res) => {});
    },

    loadHistory() {
        request
            .get(base_url + '/api/history')
            .query({
                client_id: ClientStore.getClientId()
            })
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.INIT,
                        data: {
                            request: "history",
                            orders: res.body.orders
                        }
                    });
                } else {
                    alert(res.status);
                }
            });
    },

    loadPromos() {
        request
            .get(base_url + '/api/promo/list')
            .query({
                client_id: ClientStore.getClientId()
            })
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "promos",
                            promos: res.body.promos
                        }
                    });
                } else {
                    alert(res.status);
                }
            });
    }

};

export default Actions;