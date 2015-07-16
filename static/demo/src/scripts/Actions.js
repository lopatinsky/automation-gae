import AppDispatcher from "./AppDispatcher";

const Actions = {
    INFO_UPDATED: "INFO_UPDATED",
    updateInfo(name, phone, email) {
        AppDispatcher.dispatch({
            actionType: Actions.INFO_UPDATED,
            data: { name, phone, email }
        });
    },

    EDIT_STARTED: "EDIT_STARTED",
    startEdit(itemId) {
        AppDispatcher.dispatch({
            actionType: Actions.EDIT_STARTED,
            data: itemId
        })
    },
    EDIT_FINISHED: "EDIT_FINISHED",
    finishEdit(item) {
        AppDispatcher.dispatch({
            actionType: Actions.EDIT_FINISHED,
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
    }
};

export default Actions;
