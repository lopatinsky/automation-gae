import request from 'superagent';
import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const ClientStore = new BaseStore({
    getName() {
        var name = localStorage.getItem('name');
        if (name == null) {
            name = '';
            localStorage.setItem('name', name);
        }
        return name;
    },

    getPhone() {
        var phone = localStorage.getItem('phone');
        if (phone == null) {
            phone = '';
            localStorage.setItem('phone', phone);
        }
        return phone;
    },

    getEmail() {
        var email = localStorage.getItem('email');
        if (email == null) {
            email = '';
            localStorage.setItem('email', email);
        }
        return email;
    },

    getClientId() {
        return localStorage.getItem('client_id');
    },

    getRenderedInfo() {
        var name = this.getName();
        if (name == '' || name == null) {
            return 'Представьтесь, пожалуйста';
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
            break;
        case ServerRequests.SET_CLIENT_INFO:
            ClientStore.setInfo(action.data.name, action.data.phone, action.data.email);
            break;
    }
});

export default ClientStore;