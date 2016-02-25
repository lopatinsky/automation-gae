import React from 'react';
import { HistoryStore } from '../stores';
import { Toolbar } from '../components';
import { HistoryOrderScreen } from '../components/screens';
import { ServerRequests } from '../actions';

const HistoryOrderView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _refresh() {
        this.setState({});
        this.refs.historyOrderScreen.refresh();
    },

    componentDidMount() {
        ServerRequests.loadHistory();
        HistoryStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._refresh);
    },

    toolbarLeftTap() {
        this.context.router.goBack();
    },

    render() {
        var order = HistoryStore.getOrder(this.props.params.order_id);
        return (
            <div>
                <Toolbar title='Заказ' view={this} back={true} />
                <HistoryOrderScreen order={order} ref="historyOrderScreen" />
            </div>
        );
    }
});
export default HistoryOrderView;