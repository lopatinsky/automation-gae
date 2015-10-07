import request from 'superagent';
import BaseStore from './BaseStore';
import Actions from '../Actions';

const AddressStore = new BaseStore({
    cities: [],

    _setCities(cities) {
        this.cities = cities;
        if (cities.length > 0) {
            this.setChosenCity(cities[0]);
        }
    },

    getCities() {
        return this.cities;
    },

    getChosenCity() {
        return localStorage.getItem('city');
    },

    setChosenCity(city) {
        localStorage.setItem('city', city);
    },

    getStreet() {
        return localStorage.getItem('street');
    },

    getHome() {
        return localStorage.getItem('home');
    },

    getFlat() {
        return localStorage.getItem('flat');
    },

    getCityIndex(city) {
        for (var i = 0; i < this.cities.length; i++) {
            if (city == this.cities[i]) {
                return i;
            }
        }
    },

    setAddress(street, home, flat) {
        localStorage.setItem('street', street);
        localStorage.setItem('home', home);
        localStorage.setItem('flat', flat);
        Actions.checkOrder();
        this._changed();
    },

    getAddressStr() {
        return this.getChosenCity() + ', ' + this.getStreet() + ', ' + this.getHome();
    },

    getAddressDict() {
        return {
            address: {
                city: this.getChosenCity(),
                street: this.getStreet(),
                home: this.getHome(),
                flat: this.getFlat()
            },
            coordinates: {
                lat: 0,
                lon: 0
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