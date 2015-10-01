import request from 'superagent';
import Actions from '../Actions';
import BaseStore from './BaseStore';

const AuthStore = new BaseStore({
    token: localStorage.getItem("token"),
    login: localStorage.getItem("login"),

    doLogin(login, token) {
        this.token = token;
        this.login = login;
        localStorage.setItem("token", token);
        localStorage.setItem("login", login);
        this.loggingIn = false;
        this._changed();
    },
    doLogout() {
        this.login = this.token = null;
        localStorage.removeItem("token");
        localStorage.removeItem("login");
        this._changed();
    }
}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "login") {
                AuthStore.doLogin(action.data.login, action.data.token);
            }
            if (action.data.request == "logout") {
                AuthStore.doLogout();
            }
            break;
        case Actions.AJAX_FAILURE:
            if (action.data.err.status == 401 && action.data.request != "login") {
                AuthStore.doLogout();
            }
            break;
    }
});

export default AuthStore;
