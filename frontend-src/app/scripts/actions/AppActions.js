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
        });
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
        });
    },

    SET_PAYMENT_TYPE: "SET_PAYMENT_TYPE",
    setPaymentType(paymentType) {
        AppDispatcher.dispatch({
            actionType: this.SET_PAYMENT_TYPE,
            data: {
                paymentType
            }
        });
    },

    SET_DELIVERY_TYPE: "SET_DELIVERY_TYPES",
    setDeliveryType(deliveryType) {
        AppDispatcher.dispatch({
            actionType: this.SET_DELIVERY_TYPE,
            data: {
                deliveryType
            }
        });
    },

    SET_VENUE: "SET_VENUE",
    setVenue(venue) {
        AppDispatcher.dispatch({
            actionType: this.SET_VENUE,
            data: {
                venue
            }
        });
    },

    SET_SLOT_ID: "SET_SLOT_ID",
    setSlotId(slotId) {
        AppDispatcher.dispatch({
            actionType: this.SET_SLOT_ID,
            data: {
                slotId
            }
        });
    },

    ADD_ITEM: "ADD_ITEM",
    addItem(itemId, groupModifierChoices, singleModifierQuantities) {
        AppDispatcher.dispatch({
            actionType: this.ADD_ITEM,
            data: {
                itemId,
                groupModifierChoices,
                singleModifierQuantities
            }
        });
    },

    REMOVE_ITEM: "REMOVE_ITEM",
    removeItem(orderItem) {
        AppDispatcher.dispatch({
            actionType: this.REMOVE_ITEM,
            data: {
                item: orderItem
            }
        })
    }
};

export default AppActions;
