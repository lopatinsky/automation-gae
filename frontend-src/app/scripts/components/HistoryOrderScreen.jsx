import React from 'react';
import { Card, CardText, RefreshIndicator } from 'material-ui';
import Actions from '../Actions';

const HistoryOrderScreen = React.createClass({
    getOrder() {
        var order = this.props.order;
        if (order != null) {
            return <Card>
                <CardText>
                    Заказ {order.number}
                </CardText>
            </Card>;
        } else {
             return <RefreshIndicator size={40} left={80} top={5} status="loading" />
        }
    },

    render() {
        return <div>
            {this.getOrder()}
        </div>;
    }
});

export default HistoryOrderScreen;