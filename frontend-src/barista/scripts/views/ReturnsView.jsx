import React from 'react';
import Actions from '../Actions';
import { AjaxStore, OrderStore } from '../stores';
import { OrderList } from '../components';

const ReturnsView = React.createClass({
    componentDidMount() {
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
        OrderStore.addChangeListener(this._onOrderStoreChange);
        Actions.loadReturns();
    },
    componentWillUnmount() {
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
        OrderStore.removeChangeListener(this._onOrderStoreChange);
    },
    getInitialState() {
        return {
            loading: AjaxStore.sending.returns,
            history: null
        }
    },
    _onAjaxStoreChange() {
        this.setState({
            loading: AjaxStore.sending.returns
        });
    },
    _onOrderStoreChange(data) {
        if (data && data.returns) {
            this.setState({
                returns: data.returns
            });
        }
    },
    render() {
        return <OrderList orders={this.state.returns}
                          loadedOrders={this.state.returns != null}
                          loadingOrders={this.state.loading}
                          tryReload={() => Actions.loadReturns()}
                          simple={true}/>
    }

});
export default ReturnsView;
