import React from 'react';
import { HistoryStore } from '../stores';
import { Toolbar, NavigationDrawer, HistoryOrderScreen } from '../components';
import { Navigation } from 'react-router';
import Actions from '../Actions';

const HistoryOrderView = React.createClass({
    mixins: [Navigation],

    _refresh() {
        this.setState({});
        this.refs.historyOrderScreen.refresh();
    },

    componentDidMount() {
        Actions.loadHistory();
        HistoryStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._refresh);
    },

    toolbarLeftTap() {
        this.transitionTo('history');
    },

    render() {
        var order = HistoryStore.getOrder(this.props.params.order_id);
        return (
            <div>
                <Toolbar title='Заказ' view={this} back={true} />
                <HistoryOrderScreen order={order} ref="historyOrderScreen" />
                <NavigationDrawer ref="navigationDrawer" />
            </div>
        );
    }
});
export default HistoryOrderView;