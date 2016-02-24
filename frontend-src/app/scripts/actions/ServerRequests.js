import request from 'superagent';
import AppDispatcher from "./../AppDispatcher";
import { ClientStore, VenuesStore, AddressStore, PaymentsStore, OrderStore } from '../stores';

const BASE_URL = 'http://chikarabar.m-test.doubleb-automation-production.appspot.com';
const base_url = BASE_URL;

function doRequest(id, method, url) {
    const req = request(method, BASE_URL + url);
    const _end = req.end.bind(req);
    req.end = function(makeData) {
        AppDispatcher.dispatch({
            actionType: ServerRequests.AJAX_SENDING,
            data: { request: id }
        });
        _end((err, res) => {
            if (err) {
                AppDispatcher.dispatch({
                    actionType: ServerRequests.AJAX_FAILURE,
                    data: {
                        request: id,
                        err
                    }
                })
            } else {
                AppDispatcher.dispatch({
                    actionType: ServerRequests.AJAX_SUCCESS,
                    data: Object.assign({ request: id }, makeData(res))
                })
            }
        });
    };
    return req;
}
doRequest.get = function get(id, url) {
    return doRequest(id, 'GET', url);
};
doRequest.post = function post(id, url) {
    return doRequest(id, 'POST', url);
};

const ServerRequests = {
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    sendClientInfo() {
        doRequest.post('client', '/api/client')
            .type('form')
            .send({
                client_id: ClientStore.getClientId(),
                client_name: ClientStore.getName(),
                client_phone: ClientStore.getPhone(),
                client_email: ClientStore.getEmail()
            })
            .end(res => ({}));
    },

    _loadMenu() {
        doRequest.get('menu', '/api/menu')
            .end(res => ({menu: res.body.menu}));
    },

    _loadVenues() {
        doRequest.get('venues', '/api/venues')
            .end(res => ({venues: res.body.venues}));
    },

    _loadPaymentTypes() {
        doRequest.get('payment_types', '/api/payment/payment_types')
            .end(res => ({payment_types: res.body.payment_types}));
    },

    _loadCompanyInfo() {
        doRequest.get('company', '/api/company/info')
            .end(res => ({info: res.body}));
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

    checkOrder() {
        var dict = OrderStore.getCheckOrderDict();
        if (dict) {
            request
                .post(base_url + '/api/check_order')
                .type('form')
                .send(dict)
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
                        AppDispatcher.dispatch({
                            actionType: this.AJAX_FAILURE,
                            data: {
                                request: "order"
                            }
                        });
                    }
                });
        }
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
                            request: "history",
                            order_id: order_id
                        }
                    });
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
        AppDispatcher.dispatch({
            actionType: this.AJAX_SENDING,
            data: {
                request: "history"
            }
        });
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
                    AppDispatcher.dispatch({
                        actionType: this.ERROR,
                        data: {
                            request: "history"
                        }
                    });
                }
            });
    },

    loadPromos() {
        doRequest.get('promos', '/api/promo/list')
            .query({
                client_id: ClientStore.getClientId()
            })
            .end(res => ({promos: res.body.promos}));
    }

};

export default ServerRequests;