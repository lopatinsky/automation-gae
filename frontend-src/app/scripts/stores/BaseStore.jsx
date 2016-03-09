import { EventEmitter } from 'events';
import AppDispatcher from '../AppDispatcher';

class BaseStore extends EventEmitter {
    constructor(obj, dispatchFn) {
        super();

        Object.assign(this, obj);
        this.dispatchToken = AppDispatcher.register(dispatchFn);
    }

    addChangeListener(fn) {
        this.on('change', fn);
    }

    removeChangeListener(fn) {
        this.removeListener('change', fn);
    }

    _changed(data) {
        this.emit('change', data);
    }
}
export default BaseStore;