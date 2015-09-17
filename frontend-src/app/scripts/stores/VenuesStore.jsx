import BaseStore from './BaseStore';
import Actions from '../Actions';

const VenuesStore = new BaseStore({
    chosenVenue: null,
    chosenDelivery: null,

    getChosenVenue() {
        return this.chosenVenue;
    },

    setChosenVenue(venue) {
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

    getVenues() {
        return this.venues;
    },

    _saveVenues(venues) {
        this.venues = venues;
        if (venues.length > 0) {
            this.chosenVenue = venues[0];
            if (this.chosenVenue.deliveries.length > 0) {
                this.setChosenDelivery(this.chosenVenue.deliveries[0]);
            }
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