import React from 'react';
import { Card, CardText, FontIcon } from 'material-ui';
import { HistoryStore, VenuesStore } from '../../stores';
import { ServerRequests } from '../../actions';
import { LoadingDialog } from '../dialogs'
import settings from '../../settings';

const HistoryScreen = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    _refresh() {
        if (HistoryStore.isLoading() && !HistoryStore.isOrderLoaded()) {
            this.refs.processingDialog.show();
        } else {
            this.refs.processingDialog.dismiss();
        }
        this.setState({});
    },

    _onOrderTap(order) {
        this.context.router.push(`/order/${order.id}`);
    },

    getOrders() {
        var orders = HistoryStore.getOrders();
        if (orders.length == 0) {
            return <div style={{textAlign: 'center'}}>
                История заказов пуста
            </div>;
        }
        return orders.map(order => {
            var from_title = '';
            if (order.delivery_type == 2) {
                from_title = order.address.formatted_address;
            } else {
                var venue = VenuesStore.getVenue(order.venue_id);
                if (venue != null) {
                    from_title = venue.title;
                }
            }

            return <div style={{width: '100%'}}>
                <Card
                    style={{margin: '0 12px 12px 12px'}}
                    onClick={() => this._onOrderTap(order)}>
                    <div>
                        <div style={{padding: '12px 12px 0 12px'}}>
                                <b>
                                    {'Мой заказ '}
                                    <b style={{color: settings.primaryColor}}>
                                        {'#' + order.number}
                                    </b>
                                </b>
                            <div style={{float: 'right'}}>
                                <b>{order.total} руб.</b>
                            </div>
                        </div>
                        <div style={{padding: '6px 12px 0 12px'}}>
                            {order.delivery_time_str}
                            <div style={{float: 'right'}}>
                                {HistoryStore.getStatus(order.status)}
                            </div>
                        </div>
                        <div style={{display: 'table', padding: '6px 12px 12px 12px'}}>
                            <FontIcon style={{display: 'table-cell', fontSize: '18px', verticalAlign: 'middle'}}
                                      color={settings.primaryColor}
                                      className="material-icons">
                                location_on
                            </FontIcon>
                            <div style={{display: 'table-cell', padding: '0 0 0 6px'}}>
                                {from_title}
                            </div>
                        </div>
                    </div>
                </Card>
            </div>
        })
    },

    componentDidMount() {
        ServerRequests.loadHistory();
        HistoryStore.addChangeListener(this._refresh);
        this._refresh();
    },

    componentWillUnmount() {
        HistoryStore.removeChangeListener(this._refresh);
        this.refs.processingDialog.dismiss();
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this.getOrders()}
            <LoadingDialog
                ref='processingDialog'
                title='Загрузка истории'/>
        </div>;
    }
});

export default HistoryScreen;