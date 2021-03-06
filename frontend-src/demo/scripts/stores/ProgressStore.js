import { EventEmitter } from 'events';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';
import InfoStore from './InfoStore';
import MenuStore from './MenuStore';
import VenueStore from './VenueStore';

const ProgressStore = Object.assign({}, EventEmitter.prototype, PersistenceMixin, {
    steps: {
        INFO: "INFO",
        MENU: "MENU",
        VENUE: "VENUE",
        LOADING: "LOADING",
        FINISH: "FINISH"
    },
    step: "INFO",
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    getStep() {
        return this.step;
    },
    go(step) {
        if (step in this.steps) {
            this.step = step;
            this.emit('change');
        }
    }
});
ProgressStore.initPersistence(['step'], 'progress');
ProgressStore.dispatchToken = AppDispatcher.register(function(action) {
    switch (action.actionType) {
        case Actions.GO_TO_STEP:
            ProgressStore.go(action.data);
            break;
        case Actions.RESTART:
            ProgressStore.clearPersistence();
            AppDispatcher.waitFor([MenuStore.dispatchToken, VenueStore.dispatchToken, InfoStore.dispatchToken]);
            window.location.reload();
            break;
        case Actions.POSTING_TO_SERVER:
            ProgressStore.go(ProgressStore.steps.LOADING);
            break;
        case Actions.POST_TO_SERVER_SUCCESS:
            AppDispatcher.waitFor([InfoStore.dispatchToken]);
            ProgressStore.go(ProgressStore.steps.FINISH);
            break;
    }
});

export default ProgressStore;
