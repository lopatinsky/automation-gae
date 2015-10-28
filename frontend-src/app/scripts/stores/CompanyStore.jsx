import request from 'superagent';
import BaseStore from './BaseStore';
import { ServerRequests } from '../actions';

const CompanyStore = new BaseStore({
    info: null,

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

    setInfo(info) {
        this.info = info;
    }

}, action => {
    switch (action.actionType) {
        case ServerRequests.INIT:
            if (action.data.request == "company") {
                CompanyStore.setInfo(action.data.info);
            }
            break;
    }
});

export default CompanyStore;