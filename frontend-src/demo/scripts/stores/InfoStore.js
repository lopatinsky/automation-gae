import { EventEmitter } from 'events';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';

const InfoStore = Object.assign({}, EventEmitter.prototype, PersistenceMixin, {
    name: '',
    phone: '',
    email: '',
    login: null,
    password: null,
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    updateMainInfo({name, phone, email}) {
        Object.assign(this, {name, phone, email});
        this.emit('change');
    },
    getMainInfo() {
        let {name, phone, email} = this;
        return {name, phone, email};
    },
    setLoginPassword({login, password}) {
        Object.assign(this, {login, password});
        this.emit('change');
    },
    getLoginPassword() {
        let {login, password} = this;
        return {login, password};
    }
});
InfoStore.initPersistence(['name', 'phone', 'email', 'login', 'password'], 'info');
InfoStore.dispatchToken = AppDispatcher.register(function(action) {
    switch (action.actionType) {
        case Actions.INFO_UPDATED:
            InfoStore.updateMainInfo(action.data);
            break;
        case Actions.RESTART:
            InfoStore.clearPersistence();
            break;
        case Actions.POST_TO_SERVER_SUCCESS:
            InfoStore.setLoginPassword(action.data);
            break;
    }
});

export default InfoStore;
