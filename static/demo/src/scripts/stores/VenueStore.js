import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';

const VenueStore = assign({}, EventEmitter.prototype, {
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
        assign(this, {address, lat, lng});
        this.emit('change');
    },
    getVenueInfo() {
        let {title, address, lat, lng} = this;
        return {title, address, lat, lng};
    }
});
VenueStore.dispatchToken = AppDispatcher.register(action => {
    if (action.actionType == Actions.VENUE_TITLE_UPDATED) {
        VenueStore.updateTitle(action.data);
    } else if (action.actionType == Actions.VENUE_LOCATION_UPDATED) {
        VenueStore.updateAddress(action.data);
    }
});

export default VenueStore;
