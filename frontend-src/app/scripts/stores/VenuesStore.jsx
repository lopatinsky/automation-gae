import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const VenuesStore = new BaseStore({
    venues: [],
    chosenVenue: null,
    chosenDelivery: null,

    getChosenVenue() {
        return this.chosenVenue;
    },

    setChosenVenue(venue) {
        var found = false;
        if (this.chosenDelivery != null) {
            for (var i = 0; i < venue.deliveries.length; i++) {
            if (this.chosenDelivery.id == venue.deliveries[i].id) {
                found = true;
                this.chosenDelivery = venue.deliveries[i];
            }
        }
        }
        if (found == false && venue.deliveries.length > 0) {
            this.chosenDelivery = venue.deliveries[0];
        }
        this.chosenVenue = venue;
        this._changed();
    },

    getChosenDelivery() {
        return this.chosenDelivery;
    },

    setChosenDelivery(delivery) {
        this.chosenDelivery = delivery;
        this._changed();
    },

    getSlot(slotId) {
        for (var i = 0; i < this.chosenDelivery.slots.length; i++) {
            if (slotId == this.chosenDelivery.slots[i].id) {
                return this.chosenDelivery.slots[i];
            }
        }
    },

    getVenues() {
        return this.venues;
    },

    getVenue(venueId) {
        var venues = this.getVenues();
        for (var i = 0; i < venues.length; i++) {
            if (venues[i].id == venueId) {
                return venues[i];
            }
        }
    },

    _saveVenues(venues) {
        this.venues = venues;
        if (venues.length > 0) {
            this.setChosenVenue(venues[0]);
        }
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "venues") {
                VenuesStore._saveVenues(action.data.venues);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            break;
    }
});

export default VenuesStore;