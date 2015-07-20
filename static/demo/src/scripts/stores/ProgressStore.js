import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';
import InfoStore from './InfoStore';
import MenuStore from './MenuStore';
import VenueStore from './VenueStore';

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
    switch (action.actionType) {
        case Actions.NEXT_STEP:
            ProgressStore.next();
            break;
        case Actions.PREV_STEP:
            ProgressStore.prev();
            break;
        case Actions.RESTART:
            ProgressStore.clearPersistence();
            AppDispatcher.waitFor([MenuStore.dispatchToken, VenueStore.dispatchToken, InfoStore.dispatchToken]);
            window.location.reload();
            break;
    }
});

export default ProgressStore;
