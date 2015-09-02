import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { AuthStore } from "./stores";

function authRequest(method, url) {
    return request(method, url)
        .query({token: AuthStore.token});
}

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
            .post('/api/admin/login')
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
        authRequest('POST', '/api/admin/logout')
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
    }
};

export default Actions;
