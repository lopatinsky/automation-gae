import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { AuthStore, OrderStore } from "./stores";

function authRequest(method, url) {
    return request(method, url)
        .query({token: AuthStore.token});
}
authRequest.get = function get(url) {
    return authRequest('GET', url);
};
authRequest.post = function post(url) {
    return authRequest('POST', url);
};

const BASE_URL = 'http://m-test.doubleb-automation-production.appspot.com/api/';

const Actions = {
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    login(login, password) {
        AppDispatcher.dispatch({
            actionType: this.AJAX_SENDING,
            data: { request: "login" }
        });
        request
            .post(BASE_URL + 'admin/login')
            .type('form')
            .send({ email: login, password, lat: 0, lon: 0 })
            .end((err, res) => {
                if (res.status != 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: { request: "login", status: res.status }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: { request: "login", login, token: res.body.token }
                    })
                }
            });
    },

    logout(password) {
        AppDispatcher.dispatch({
            actionType: this.AJAX_SENDING,
            data: { request: "logout" }
        });
        authRequest.post(BASE_URL + 'admin/logout')
            .type('form')
            .send({ password })
            .end((err, res) => {
                if (res.status != 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: { request: "logout", status: res.status }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: { request: "logout" }
                    })
                }
            });
    },

    loadCurrent() {
        AppDispatcher.dispatch({
            actionType: this.AJAX_SENDING,
            data: { request: "current" }
        });
        authRequest.get(BASE_URL + 'admin/orders/current')
            .end((err, res) => {
                if (res.status != 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: { request: "current", status: res.status }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "current",
                            orders: res.body.orders,
                            timestamp: res.body.timestamp
                        }
                    })
                }
            });
    },

    loadUpdates() {
        AppDispatcher.dispatch({
            actionType: this.AJAX_SENDING,
            data: { request: "updates" }
        });
        authRequest.get(BASE_URL + 'admin/orders/updates')
            .query({ timestamp: OrderStore.lastServerTimestamp })
            .end((err, res) => {
                if (res.status != 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: { request: "updates", status: res.status }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "updates",
                            new_orders: res.body.new_orders,
                            updated: res.body.updated,
                            timestamp: res.body.timestamp
                        }
                    })
                }
            })
    }
};

export default Actions;
