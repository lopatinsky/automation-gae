import request from 'superagent';
import AppDispatcher from "./AppDispatcher";

const Actions = {
    INIT: "INIT",
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    loadMenu() {
        request
            .get('/api/menu')
            .end((err, res) => {
                if (res.status == 200) {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_SUCCESS,
                        data: {
                            request: "menu",
                            menu: res.body.menu
                        }
                    })
                } else {
                    AppDispatcher.dispatch({
                        actionType: this.AJAX_FAILURE,
                        data: {
                            request: "menu"
                        }
                    })
                }
            });

    },

    setMenuItem(item) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "menu_item",
                item: item
            }
        })
    }

};

export default Actions;