import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { OrderStore } from '../stores';
import Actions from '../Actions';

const OrderMenuItem = React.createClass({
    render() {
        var item = this.props.item;
        return (
            <Card>
                <CardText>
                    {item.title}
                </CardText>
            </Card>
        );
    }
});

export default OrderMenuItem;