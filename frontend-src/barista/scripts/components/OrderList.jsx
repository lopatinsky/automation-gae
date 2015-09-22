import React from 'react';
import moment from 'moment';
import OrderCard from './OrderCard';

const CurrentTimeLine = React.createClass({
    contextTypes: {
        muiTheme: React.PropTypes.object
    },
    render() {
        const style = {
            height: 4,
            margin: '0 12px 12px',
            background: this.context.muiTheme.palette.primary2Color
        };
        return <div style={style}/>
    }
});

const OrderList = React.createClass({
    _updateInterval: null,

    getInitialState() {
        return {
            time: moment()
        }
    },
    componentDidMount() {
        this._updateInterval = setInterval(() => this.setState({ time: moment() }), 5000);
    },
    componentWillUnmount() {
        clearInterval(this._updateInterval);
    },

    render() {
        const actions = {};
        for (let [key, value] of Object.entries(this.props)) {
            if (key.substring(0, 10) == "onTouchTap") {
                actions[key] = value;
            }
        }
        const orders = this.props.orders.map(
                order => <OrderCard key={order.id}
                                    order={order}
                                    {...actions}/>
        );

        let linePosition = 0;
        while (linePosition < this.props.orders.length &&
                this.props.orders[linePosition].deliveryTime.isBefore(this.state.currentTime)) {
            ++ linePosition;
        }
        orders.splice(linePosition, 0, <CurrentTimeLine key='line'/>);

        return <div style={{overflow: 'hidden'}}>
            {orders}
        </div>;
    }
});
export default OrderList;
