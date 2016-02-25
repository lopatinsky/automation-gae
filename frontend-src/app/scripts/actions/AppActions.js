import AppDispatcher from "./../AppDispatcher";
import { ServerRequests } from '../actions';

const AppActions = {
    INIT: "INIT",

    load() {
        ServerRequests._registerClient();
        ServerRequests._loadVenues();
        ServerRequests._loadMenu();
        ServerRequests._loadPaymentTypes();
        ServerRequests._loadCompanyInfo();
        ServerRequests.loadPromos();
    },

    setClientInfo(name, phone, email) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: 'client',
                name: name,
                phone: phone,
                email: email
            }
        })
    },

    setMenuItem(item) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "menu_item",
                item: item
            }
        })
    },

    setModifier(modifier) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "modifier",
                modifier: modifier
            }
        })
    },

    SET_ADDRESS: "SET_ADDRESS",
    setAddress({city, street, home, flat}) {
        AppDispatcher.dispatch({
            actionType: this.SET_ADDRESS,
            data: {
                address: {
                    city, street, home, flat
                }
            }
        });
    }
};

export default AppActions;