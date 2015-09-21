import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { ClientStore } from './stores';

const base_url = "http://mycompany.app.doubleb-automation-production.appspot.com";

const Actions = {
    INIT: "INIT",
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    load() {
        this._registerClient();
        this._loadVenues();
        this._loadMenu();
    },

    sendClientInfo() {
        request
            .post(base_url + '/api/client')
            .send({
                client_id: ClientStore.getClientId(),
                client_name: ClientStore.getName(),
                client_phone: ClientStore.getPhone(),
                client_email: ClientStore.getEmail()
            })
            .end((err, res) => {
                if (res.status == 200) {
                    alert("Client info is saved");
                }
            });
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
    }

};

export default Actions;