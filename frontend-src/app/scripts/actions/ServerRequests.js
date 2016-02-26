import request from 'superagent';
import AppDispatcher from "./../AppDispatcher";
import { ClientStore, VenuesStore, AddressStore, PaymentsStore, OrderStore } from '../stores';

const BASE_URL = 'http://chikarabar.m-test.doubleb-automation-production.appspot.com';

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

    sendClientInfo(name, phone, email) {
        doRequest.post('client', '/api/client')
            .type('form')
            .send({
                client_id: ClientStore.getClientId(),
                client_name: name,
                client_phone: phone,
                client_email: email
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
        doRequest.post('register', '/api/register')
            .query({ client_id: ClientStore.getClientId() })
            .end(res => ({
                client_id: res.body.client_id
            }));
    },

    checkOrder() {
        var dict = OrderStore.getCheckOrderDict();
        if (dict) {
            doRequest.post('checkOrder', '/api/check_order')
                .type('form')
                .send(dict)
                .end(res => ({
                    total_sum: res.body.total_sum,
                    delivery_sum: res.body.delivery_sum,
                    delivery_sum_str: res.body.delivery_sum_str,
                    promos: res.body.promos,
                    errors: res.body.errors,
                    orderGifts: res.body.new_order_gifts
                }));
        }
    },

    order() {
        doRequest.post('order', '/api/order')
            .type('form')
            .send({
                order: JSON.stringify(OrderStore.getOrderDict())
            })
            .end(res => ({
                orderId: res.body.order_id
            }));
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
        doRequest.post('', '/api/set_order_success')
            .type('form')
            .send({
                order_id: orderId
            })
            .end(res => ({}));
    },

    loadHistory() {
        doRequest.get('history', '/api/history')
            .query({
                client_id: ClientStore.getClientId()
            })
            .end(res => ({orders: res.body.orders}));
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