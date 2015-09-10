import request from 'superagent';
import AppDispatcher from "./AppDispatcher";

const Actions = {
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    loadMenu() {
         request
            .post('/api/menu')
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
    }
};
