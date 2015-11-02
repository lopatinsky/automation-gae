import React from 'react';
import Actions from '../Actions';
import { AjaxStore, OrderStore } from '../stores';
import { OrderList } from '../components';

const HistoryView = React.createClass({
    componentDidMount() {
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
        OrderStore.addChangeListener(this._onOrderStoreChange);
        Actions.loadHistory();
    },
    componentWillUnmount() {
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
        OrderStore.removeChangeListener(this._onOrderStoreChange);
    },
    getInitialState() {
        return {
            loading: AjaxStore.sending.history,
            history: null
        }
    },
    _onAjaxStoreChange() {
        this.setState({
            loading: AjaxStore.sending.history
        });
    },
    _onOrderStoreChange(data) {
        if (data && data.history) {
            this.setState({
                history: data.history
            });
        }
    },
    render() {
        return <OrderList orders={this.state.history}
                          loadedOrders={this.state.history != null}
                          loadingOrders={this.state.loading}
                          tryReload={() => Actions.loadHistory()}
                          simple={true}/>
    }

});
export default HistoryView;
