import request from 'superagent';
import AppDispatcher from "./AppDispatcher";

const base_url = "http://mycompany.app.doubleb-automation-production.appspot.com";

const Actions = {
    INIT: "INIT",
    AJAX_SENDING: "AJAX_SENDING",
    AJAX_SUCCESS: "AJAX_SUCCESS",
    AJAX_FAILURE: "AJAX_FAILURE",

    loadMenu() {
        request
            .get(base_url + '/api/menu')
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
    },

    setModifier(modifier) {
        AppDispatcher.dispatch({
            actionType: this.INIT,
            data: {
                request: "modifier",
                modifier: modifier
            }
        })
    }

};

export default Actions;