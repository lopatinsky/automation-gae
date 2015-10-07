import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { AuthStore, OrderStore, SystemStore } from "./stores";

const BASE_URL = '/api/';

function doRequest(id, method, url) {
    const req = request(method, BASE_URL + url);
    if (AuthStore.token) {
        req.query({token: AuthStore.token});
    }
    const _end = req.end.bind(req);
    req.end = function(makeData) {
        AppDispatcher.dispatch({
            actionType: Actions.AJAX_SENDING,
            data: { request: id }
        });
        _end((err, res) => {
            if (err) {
                AppDispatcher.dispatch({
                    actionType: Actions.AJAX_FAILURE,
                    data: {
                        request: id,
                        err
                    }
                })
            } else {
                AppDispatcher.dispatch({
                    actionType: Actions.AJAX_SUCCESS,
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

const Actions = {
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    login(login, password) {
        doRequest.post("login", 'admin/login')
            .type('form')
            .send({ email: login, password, lat: 0, lon: 0 })
            .end(res => ({ login, token: res.body.token }));
    },

    logout(password) {
        doRequest.post("logout", 'admin/logout')
            .type('form')
            .send({ password })
            .end(res => ({}));
    },

    loadDeliveryTypes() {
        doRequest.get("delivery_types", 'admin/delivery_types')
            .end(res => ({
                deliveries: res.body.deliveries
            }));
    },

    loadCurrent() {
        doRequest.get("current", 'admin/orders/current')
            .end(res => ({
                orders: res.body.orders,
                timestamp: res.body.timestamp
            }));
    },

    loadUpdates() {
        doRequest.get("updates", 'admin/orders/updates')
            .query({ timestamp: OrderStore.lastServerTimestamp })
            .end(res => ({
                new_orders: res.body.new_orders,
                updated: res.body.updated,
                timestamp: res.body.timestamp
            }));
    },

    cancelOrder(order, comment) {
        doRequest.post(`order_action_${order.id}`, `admin/orders/${order.id}/cancel`)
            .type('form')
            .send({ comment })
            .end(res => ({ order, action: 'cancel' }));
    },

    confirmOrder(order) {
        doRequest.post(`order_action_${order.id}`, `admin/orders/${order.id}/confirm`)
            .end(res => ({ order, action: 'confirm' }));
    },

    doneOrder(order) {
        doRequest.post(`order_action_${order.id}`, `admin/orders/${order.id}/close`)
            .end(res => ({ order, action: 'close' }));
    },

    postponeOrder(order, mins) {
        doRequest.post(`order_action_${order.id}`, `admin/orders/${order.id}/postpone`)
            .type('form')
            .send({ mins })
            .end(res => ({ order, action: 'postpone', options: { mins } }));
    },

    INIT_APP: "INIT_APP",
    initApp() {
        AppDispatcher.dispatch({
            actionType: this.INIT_APP,
            data: null
        })
    },
};

export default Actions;
