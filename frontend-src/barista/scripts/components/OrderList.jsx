import React from 'react';
import moment from 'moment';
import RaisedButton from 'material-ui/lib/raised-button';
import CircularProgress from 'material-ui/lib/circular-progress';
import Colors from 'material-ui/lib/styles/colors';
import OrderCard from './OrderCard';

const CurrentTimeLine = React.createClass({
    contextTypes: {
        muiTheme: React.PropTypes.object
    },
    render() {
        const style = {
            height: 4,
            margin: '0 12px 12px',
            background: this.context.muiTheme.rawTheme.palette.primary2Color
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
    _getHighlightColor(order) {
        const msRemain = order.deliveryTime.diff(this.state.time);
        if (msRemain > 5 * 60 * 1000) {
            return Colors.white;
        } else if (msRemain > 0) {
            return Colors.yellow300;
        } else if (msRemain > -5 * 60 * 1000) {
            return Colors.orange300;
        } else {
            return Colors.red400;
        }
    },

    _renderLoaded() {
        const actions = {};
        for (let [key, value] of Object.entries(this.props)) {
            if (key.substring(0, 10) == "onTouchTap") {
                actions[key] = value;
            }
        }
        const orders = this.props.orders.map(
                order => <OrderCard key={order.id}
                                    order={order}
                                    highlightColor={this._getHighlightColor(order)}
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
    },

    _renderLoading() {
        return <div style={{textAlign: 'center'}}>
            <CircularProgress size={2}/>
        </div>;
    },

    _renderFailed() {
        return <div style={{textAlign: 'center'}}>
            <div>Не удалось загрузить заказы.</div>
            <RaisedButton secondary={true} onTouchTap={this.props.tryReload} label='Попробовать снова'/>
        </div>
    },

    render() {
        if (this.props.loadedOrders) {
            return this._renderLoaded();
        } else if (this.props.loadingOrders) {
            return this._renderLoading();
        } else {
            return this._renderFailed();
        }
    }
});
export default OrderList;
