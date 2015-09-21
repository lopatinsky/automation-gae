import request from 'superagent';
import BaseStore from './BaseStore';
import Actions from '../Actions';

const ClientStore = new BaseStore({
    name: '',
    phone: '',
    email: '',

    getName() {
        return this.name;
    },

    getPhone() {
        return this.phone;
    },

    getEmail() {
        return this.email;
    },

    setInfo(name, phone, email) {
        this.name = name;
        this.phone = phone;
        this.email = email;
    },

    setClientId(client_id) {
        localStorage.setItem("client_id", client_id);
    },

    getClientId() {
        return localStorage.getItem("client_id");
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
    }
});

export default ClientStore;