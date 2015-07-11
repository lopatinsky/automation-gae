import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';

const InfoStore = assign({}, EventEmitter.prototype, {
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
InfoStore.dispatchToken = AppDispatcher.register(function(action) {
    if (action.actionType == Actions.INFO_UPDATED) {
        InfoStore.updateMainInfo(action.data);
    }
});

export default InfoStore;
