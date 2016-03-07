import React from 'react';
import { HistoryStore } from '../stores';
import { Toolbar } from '../components';
import { HistoryOrderScreen } from '../components/screens';
import { ServerRequests } from '../actions';

const HistoryOrderView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    componentDidMount() {
        if (!HistoryStore.isOrderLoaded() || !HistoryStore.getOrder()) {
            ServerRequests.loadHistory();
        }
    },

    toolbarLeftTap() {
        this.context.router.goBack();
    },

    render() {
        return (
            <div>
                <Toolbar title='Заказ' view={this} back={true} />
                <HistoryOrderScreen orderId={this.props.params.order_id}/>
            </div>
        );
    }
});
export default HistoryOrderView;