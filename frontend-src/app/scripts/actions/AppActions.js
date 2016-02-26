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

    SET_CLIENT_INFO: "SET_CLIENT_INFO",
    setClientInfo(name, phone, email) {
        ServerRequests.sendClientInfo(name, phone, email);
        AppDispatcher.dispatch({
            actionType: this.SET_CLIENT_INFO,
            data: {
                name,
                phone,
                email
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
    },

    SET_COMMENT: "SET_COMMENT",
    setComment(comment) {
        AppDispatcher.dispatch({
            actionType: this.SET_COMMENT,
            data: {
                comment
            }
        })
    },

    SET_PAYMENT_TYPE: "SET_PAYMENT_TYPE",
    setPaymentType(paymentType) {
        AppDispatcher.dispatch({
            actionType: this.SET_PAYMENT_TYPE,
            data: {
                paymentType
            }
        })
    }
};

export default AppActions;