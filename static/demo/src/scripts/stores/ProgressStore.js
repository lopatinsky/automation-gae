import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';

const ProgressStore = assign({}, EventEmitter.prototype, PersistenceMixin, {
    step: 0,
    minStep: 0,
    maxStep: 3,
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    getStep() {
        return this.step;
    },
    next() {
        if (this.step < this.maxStep) {
            this.step += 1;
            this.emit('change');
        }
    },
    prev() {
        if (this.step > this.minStep) {
            this.step -= 1;
            this.emit('change');
        }
    }
});
ProgressStore.initPersistence(['step'], 'progress');
ProgressStore.dispatchToken = AppDispatcher.register(function(action) {
    if (action.actionType == Actions.NEXT_STEP) {
        ProgressStore.next();
    } else if (action.actionType == Actions.PREV_STEP) {
        ProgressStore.prev();
    }
});

export default ProgressStore;
