import request from 'superagent';
import AppDispatcher from "./AppDispatcher";
import { ClientStore, VenuesStore, AddressStore, PaymentsStore,OrderStore } from './stores';

const base_url = "http://mycompany.app.doubleb-automation-production.appspot.com";

const Actions = {
    INIT: "INIT",
    UPDATE: "UPDATE",
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
            .send({
                client_id: ClientStore.getClientId(),
                delivery_type: VenuesStore.getChosenDelivery().id,
                address: JSON.stringify(AddressStore.getAddressDict()),
                venue_id: VenuesStore.getChosenVenue().id,
                payment: JSON.stringify(PaymentsStore.getPaymentDict()),
                delivery_slot_id: OrderStore.getSlotId(),
                //time_picker_value: '',
                items: JSON.stringify(OrderStore.getItemsDict())
            })
            .end((err, res) => {
                if (res.status == 200) {
                    if (res.body.valid) {
                        AppDispatcher.dispatch({
                        actionType: this.UPDATE,
                        data: {
                            request: "order",
                            total_sum: res.body.total_sum,
                            delivery_sum: res.body.delivery_sum,
                            delivery_sum_str: res.body.delivery_sum_str,
                            promos: res.body.promos
                        }
                    });
                    } else {
                        alert(res.body.errors[0]);
                    }
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
                if (res.status == 200) {

                } else {
                    alert(res.status);
                }
            });
    }
};

export default Actions;