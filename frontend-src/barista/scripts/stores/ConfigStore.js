import Actions from '../Actions';
import BaseStore from './BaseStore';
import OrderStore from './OrderStore';

const CONFIG_APP_KIND = {
    AUTO_APP: 0,
    RESTO_APP: 1
};

const ConfigStore = new BaseStore({
    APP_KIND: CONFIG_APP_KIND,

    orderAheadEnabled: true,
    deliveryEnabled: true,
    appKind: CONFIG_APP_KIND.AUTO_APP,
    venues: [],
    thisVenue: null,
    resetConfig() {
        this.orderAheadEnabled = true;
        this.deliveryEnabled = true;
        this.appKind = this.APP_KIND.AUTO_APP;
        this.venues = [];
        this.thisVenue = null;
        this._changed();
    },
    setConfig(config) {
        this.appKind = config.app_kind;
        this.orderAheadEnabled = false;
        this.deliveryEnabled = false;
        for (let delivery of config.delivery_types) {
            if (delivery != OrderStore.DELIVERY_TYPE.DELIVERY) {
                this.orderAheadEnabled = true;
            } else {
                this.deliveryEnabled = true;
            }
        }
        this.venues = config.venues;
        this.thisVenue = config.venue_id;
        this._changed();
    }
}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SUCCESS:
            if (action.data.request == "config") {
                ConfigStore.setConfig(action.data.config);
            }
            if (action.data.request == "logout") {
                ConfigStore.resetConfig();
            }
            break;
    }
});
export default ConfigStore;
