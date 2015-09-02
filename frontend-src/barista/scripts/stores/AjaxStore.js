import Actions from '../Actions';
import BaseStore from './BaseStore';

const AjaxStore = new BaseStore({
    sending: {},
    started(requestId) {
        this.sending[requestId] = true;
        this._changed();
    },
    succeeded(requestId) {
        delete this.sending[requestId];
        this._changed();
    },
    failed(requestId, status) {
        delete this.sending[requestId];
        this._changed({requestId, status})
    }
}, action => {
    switch (action.actionType) {
        case Actions.AJAX_SENDING:
            AjaxStore.started(action.data.request);
            break;
        case Actions.AJAX_SUCCESS:
            AjaxStore.succeeded(action.data.request);
            break;
        case Actions.AJAX_FAILURE:
            AjaxStore.failed(action.data.request, action.data.status);
            break;
    }
});
export default AjaxStore;
