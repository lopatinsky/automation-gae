import request from 'superagent';
import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const ClientStore = new BaseStore({
    getName() {
        return localStorage.getItem('name');
    },

    getPhone() {
        return localStorage.getItem('phone');
    },

    getEmail() {
        return localStorage.getItem('email');
    },

    getClientId() {
        return localStorage.getItem('client_id');
    },

    getRenderedInfo() {
        var name = this.getName();
        if (name == '' || name == null) {
            return 'Представтесь, пожалуйста';
        } else {
            return name;
        }
    },

    setInfo(name, phone, email) {
        localStorage.setItem('name', name);
        localStorage.setItem('phone', phone);
        localStorage.setItem('email', email);
        this._changed();
    },

    setClientId(client_id) {
        localStorage.setItem("client_id", client_id);
    },

    getClientId() {
        return localStorage.getItem("client_id");
    },

    getClientDict() {
        return {
            id: this.getClientId(),
            name: this.getName(),
            phone: this.getPhone(),
            email: this.getEmail()
        }
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "register") {
                ClientStore.setClientId(action.data.client_id);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            alert("Failure");
            break;
        case ServerRequests.INIT:
            if (action.data.request == "client") {
                ClientStore.setInfo(action.data.name, action.data.phone, action.data.email);
            }
            break;
    }
});

export default ClientStore;