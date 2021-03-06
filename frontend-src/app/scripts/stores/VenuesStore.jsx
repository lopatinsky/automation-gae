import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const VenuesStore = new BaseStore({
    venues: [],

    getVenue(venueId) {
        for (let venue of this.venues) {
            if (venue.id == venueId) {
                return venue;
            }
        }
    },

    _saveVenues(venues) {
        this.venues = venues;
        this._changed();
    }
}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "venues") {
                VenuesStore._saveVenues(action.data.venues);
            }
            break;
    }
});

export default VenuesStore;