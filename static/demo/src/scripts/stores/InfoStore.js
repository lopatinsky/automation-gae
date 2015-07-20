import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';

const InfoStore = assign({}, EventEmitter.prototype, PersistenceMixin, {
    name: '',
    phone: '',
    email: '',
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    updateMainInfo({name, phone, email}) {
        assign(this, {name, phone, email});
        this.emit('change');
    },
    getMainInfo() {
        let {name, phone, email} = this;
        return {name, phone, email};
    }
});
InfoStore.initPersistence(['name', 'phone', 'email'], 'info');
InfoStore.dispatchToken = AppDispatcher.register(function(action) {
    switch (action.actionType) {
        case Actions.INFO_UPDATED:
            InfoStore.updateMainInfo(action.data);
            break;
        case Actions.RESTART:
            InfoStore.clearPersistence();
            break;
    }
});

export default InfoStore;
