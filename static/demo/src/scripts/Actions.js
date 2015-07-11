import AppDispatcher from "./AppDispatcher";

const Actions = {
    INFO_UPDATED: "INFO_UPDATED",

    updateInfo(name, phone, email) {
        AppDispatcher.dispatch({
            actionType: Actions.INFO_UPDATED,
            data: { name, phone, email }
        });
    }
};

export default Actions;
