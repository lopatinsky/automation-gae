import request from 'superagent';
import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const CompanyStore = new BaseStore({
    info: null,

    getDeliveryTypes() {
        if (this.info) {
            return this.info.delivery_types;
        }
        return [];
    },

    getSlot(deliveryType, slotId) {
        for (var i = 0; i < deliveryType.slots.length; i++) {
            if (slotId == deliveryType.slots[i].id) {
                return deliveryType.slots[i];
            }
        }
    },

    getEmails() {
        var emails = '';
        if (this.info != null) {
            for (var i = 0; i < this.info.emails.length; i++) {
                if (this.info.emails[i]) {
                    emails += this.info.emails[i] + ',';
                }
            }
        }
        return emails;
    },

    getName() {
        if (this.info != null ) {
            return this.info.app_name;
        }
        return '';
    },

    getSite() {
        if (this.info != null) {
            let site = this.info.site;
            if (site && site.substr(0, 4) != 'http') {
                site = 'http://' + site;
            }
            return site;
        }
        return '';
    },

    setInfo(info) {
        this.info = info;
        this._changed();
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.AJAX_SUCCESS:
            if (action.data.request == "company") {
                CompanyStore.setInfo(action.data.info);
            }
            break;
    }
});

export default CompanyStore;