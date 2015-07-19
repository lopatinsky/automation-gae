import AppDispatcher from "./AppDispatcher";

const Actions = {
    INFO_UPDATED: "INFO_UPDATED",
    updateInfo(name, phone, email) {
        AppDispatcher.dispatch({
            actionType: Actions.INFO_UPDATED,
            data: { name, phone, email }
        });
    },

    ITEM_EDIT_STARTED: "ITEM_EDIT_STARTED",
    startEditItem(itemId) {
        AppDispatcher.dispatch({
            actionType: Actions.ITEM_EDIT_STARTED,
            data: itemId
        })
    },
    ITEM_EDIT_FINISHED: "ITEM_EDIT_FINISHED",
    finishEditItem(item) {
        AppDispatcher.dispatch({
            actionType: Actions.ITEM_EDIT_FINISHED,
            data: item
        })
    },
    EDIT_CANCELED: "EDIT_CANCELED",
    cancelEdit() {
        AppDispatcher.dispatch({
            actionType: Actions.EDIT_CANCELED,
            data: null
        })
    },
    ITEM_ADDED: "ITEM_ADDED",
    addItem(categoryId) {
        AppDispatcher.dispatch({
            actionType: Actions.ITEM_ADDED,
            data: categoryId
        })
    },

    CATEGORY_EDIT_STARTED: "CATEGORY_EDIT_STARTED",
    startEditCategory(categoryId) {
        AppDispatcher.dispatch({
            actionType: Actions.CATEGORY_EDIT_STARTED,
            data: categoryId
        })
    },
    CATEGORY_EDIT_FINISHED: "CATEGORY_EDIT_FINISHED",
    finishEditCategory(category) {
        AppDispatcher.dispatch({
            actionType: Actions.CATEGORY_EDIT_FINISHED,
            data: category
        });
    },
    CATEGORY_ADDED: "CATEGORY_ADDED",
    addCategory() {
        AppDispatcher.dispatch({
            actionType: Actions.CATEGORY_ADDED,
            data: null
        })
    },

    VENUE_TITLE_UPDATED: "VENUE_TITLE_UPDATED",
    updateVenueTitle(title) {
        AppDispatcher.dispatch({
            actionType: Actions.VENUE_TITLE_UPDATED,
            data: title
        })
    },
    VENUE_LOCATION_UPDATED: "VENUE_LOCATION_UPDATED",
    updateVenueLocation(location) {
        AppDispatcher.dispatch({
            actionType: Actions.VENUE_LOCATION_UPDATED,
            data: location
        })
    },

    NEXT_STEP: "NEXT_STEP",
    nextStep() {
        AppDispatcher.dispatch({
            actionType: Actions.NEXT_STEP,
            data: null
        })
    },
    PREV_STEP: "PREV_STEP",
    prevStep() {
        AppDispatcher.dispatch({
            actionType: Actions.PREV_STEP,
            data: null
        })
    }
};

export default Actions;
