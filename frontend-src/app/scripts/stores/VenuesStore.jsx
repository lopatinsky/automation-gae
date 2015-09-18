import BaseStore from './BaseStore';
import Actions from '../Actions';

const VenuesStore = new BaseStore({
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

    getSlotIndex(slot_id) {
        for (var i = 0; i < this.chosenDelivery.slots.length; i++) {
            if (slot_id == this.chosenDelivery.slots[i].id) {
                return i;
            }
        }
    },

    getVenues() {
        return this.venues;
    },

    _saveVenues(venues) {
        this.venues = venues;
        if (venues.length > 0) {
            this.setChosenVenue(venues[0]);
        }
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "venues") {
                VenuesStore._saveVenues(action.data.venues);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert('failure');
            break;
    }
});

export default VenuesStore;