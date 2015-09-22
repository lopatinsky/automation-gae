import request from 'superagent';
import BaseStore from './BaseStore';
import Actions from '../Actions';

const AddressStore = new BaseStore({
    cities: [],
    city: '',
    street: '',
    home: '',
    flat: '',

    _setCities(cities) {
        this.cities = cities;
        if (cities.length > 0) {
            this.city = cities[0];
        }
    },

    getCities() {
        return this.cities;
    },

    getChosenCity() {
        return this.city;
    },

    setChosenCity(city) {
        this.city = city;
    },

    getStreet() {
        return this.street;
    },

    getHome() {
        return this.home;
    },

    getFlat() {
        return this.flat;
    },

    getCityIndex(city) {
        for (var i = 0; i < this.cities.length; i++) {
            if (city == this.cities[i]) {
                return i;
            }
        }
    },

    setAddress(street, home, flat) {
        this.street = street;
        this.home = home;
        this.flat = flat;
        this._changed();
    },

    getAddressStr() {
        return this.city + ', ' + this.street + ', ' + this.home;
    },

    getAddressDict() {
        return {
            address: {
                city: this.getChosenCity(),
                street: this.getStreet(),
                home: this.getHome(),
                flat: this.getFlat()
            }
        }
    }

}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "address") {
                AddressStore._setCities(action.data.cities);
            }
            break;
        case Actions.AJAX_FAILURE:
            alert("Failure");
            break;
    }
});

export default AddressStore;