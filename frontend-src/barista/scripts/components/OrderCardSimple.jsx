import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import { OrderInfo } from '../components';

const OrderCard = React.createClass({
    render() {
        return <Card style={{margin:'0 12px 12px', fontWeight: 300}}>
            <CardText>
                <OrderInfo order={this.props.order}
                           highlightColor={this.props.highlightColor}/>
            </CardText>
        </Card>;
    }
});
export default OrderCard;
