import request from 'superagent';
import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const AddressStore = new BaseStore({
    cities: [],

    _setCities(cities) {
        this.cities = cities;
        if (cities.length > 0 && this.getChosenCity() == '') {
            this.setChosenCity(cities[0]);
        }
        this._changed();
    },

    getCities() {
        return this.cities;
    },

    getChosenCity() {
        var city = localStorage.getItem('city');
        if (city == null) {
            city = '';
            localStorage.setItem('city', city);
        }
        return city;
    },

    setChosenCity(city) {
        localStorage.setItem('city', city);
        ServerRequests.checkOrder();
        this._changed();
    },

    getStreet() {
        var street = localStorage.getItem('street');
        if (street == null) {
            street = '';
            localStorage.setItem('street', street);
        }
        return street;
    },

    getHome() {
        var home = localStorage.getItem('home');
        if (home == null) {
            home = '';
            localStorage.setItem('home', home);
        }
        return home;
    },

    getFlat() {
        var flat = localStorage.getItem('flat');
        if (flat == null) {
            flat = '';
            localStorage.setItem('flat', flat);
        }
        return flat;
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
        ServerRequests.checkOrder();
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
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "address") {
                AddressStore._setCities(action.data.cities);
            }
            break;
        case ServerRequests.AJAX_FAILURE:
            alert("Failure");
            break;
    }
});

export default AddressStore;