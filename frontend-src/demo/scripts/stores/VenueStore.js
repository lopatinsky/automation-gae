import { EventEmitter } from 'events';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';

const VenueStore = Object.assign({}, EventEmitter.prototype, PersistenceMixin, {
    title: '',
    address: '',
    lat: null,
    lng: null,
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    updateTitle(title) {
        this.title = title;
        this.emit('change');
    },
    updateAddress({address, lat, lng}) {
        Object.assign(this, {address, lat, lng});
        this.emit('change');
    },
    getVenueInfo() {
        let {title, address, lat, lng} = this;
        return {title, address, lat, lng};
    }
});
VenueStore.initPersistence(['title', 'address', 'lat', 'lng'], 'venue');
VenueStore.dispatchToken = AppDispatcher.register(action => {
    switch (action.actionType) {
        case Actions.VENUE_TITLE_UPDATED:
            VenueStore.updateTitle(action.data);
            break;
        case Actions.VENUE_LOCATION_UPDATED:
            VenueStore.updateAddress(action.data);
            break;
        case Actions.RESTART:
            VenueStore.clearPersistence();
            break;
    }
});

export default VenueStore;
