import React from 'react';
import AppBar from 'material-ui/lib/app-bar';
import Colors from 'material-ui/lib/styles/colors';
import FlatButton from 'material-ui/lib/flat-button';
import FontIcon from 'material-ui/lib/font-icon';
import IconButton from 'material-ui/lib/icon-button';
import NavigationChevronLeft from 'material-ui/lib/svg-icons/navigation/chevron-left';
import { OrderStore, MenuStore } from '../stores';

const Toolbar = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
        location: React.PropTypes.object.isRequired
    },

    ORDER_BUTTON: 'order',

    getInitialState() {
        return {
            orderTotal: OrderStore.getTotalSum()
        };
    },

    _onOrderChangeListener() {
        this.setState({
            orderTotal: OrderStore.getTotalSum()
        });
    },

    leftTap() {
        this.props.view.toolbarLeftTap();
    },

    rightTap() {
        if (this.props.right == this.ORDER_BUTTON) {
            this.context.router.push('order');
        }
    },

    componentDidMount() {
        OrderStore.addChangeListener(this._onOrderChangeListener);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._onOrderChangeListener);
    },

    render() {
        var rightElement;
        if (this.props.right == this.ORDER_BUTTON) {
            let icon = <FontIcon className="material-icons">shopping_basket</FontIcon>;
            var label = this.state.orderTotal + " руб.";
            rightElement = <FlatButton onTouchTap={this.rightTap} label={label} icon={icon}/>;
        }
        var leftElement;
        if (this.props.back == true) {
            leftElement = <IconButton onTouchTap={this.leftTap}>
                <NavigationChevronLeft/>
            </IconButton>;
        }
        return (
            <AppBar
                style={{position: 'fixed', height: '64px', zIndex: '4'}}
                title={this.props.title}
                onLeftIconButtonTouchTap={this.leftTap}
                iconElementLeft={leftElement}
                iconElementRight={rightElement} />
        );
    }
});

export default Toolbar;