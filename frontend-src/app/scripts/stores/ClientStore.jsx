import request from 'superagent';
import BaseStore from './BaseStore';
import Actions from '../Actions';

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

    getCLientDict() {
        return {
            id: this.getClientId(),
            name: this.getName(),
            phone: this.getPhone(),
            email: this.getEmail()
        }
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "register") {
                ClientStore.setClientId(action.data.client_id);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert("Failure");
            break;
        case Actions.INIT:
            ClientStore.setInfo(action.data.name, action.data.phone, action.data.email);
            break;
    }
});

export default ClientStore;