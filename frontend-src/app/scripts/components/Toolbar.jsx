import React from 'react';
import { AppBar, IconButton, FlatButton, Icons } from 'material-ui';
import { Navigation } from 'react-router';
import { OrderStore } from '../stores';

const Toolbar = React.createClass({
    ORDER_BUTTON: 'order',

    mixins: [Navigation],

    _refresh() {
        this.setState({});
    },

    leftTap() {
        this.props.view.toolbarLeftTap();
    },

    rightTap() {
        if (this.props.right == this.ORDER_BUTTON) {
            this.transitionTo('order');
        }
    },

    componentDidMount() {
        OrderStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._refresh);
    },

    render() {
        var rightElement;
        if (this.props.right == this.ORDER_BUTTON) {
            var label = "Sum: " + OrderStore.getTotalSum();
            rightElement = <FlatButton label={label}  onClick={this.rightTap} />;
        }
        var leftElement;
        if (this.props.back == true) {
            leftElement = <IconButton onClick={this.leftTap}>
                <Icons.NavigationChevronLeft/>
            </IconButton>;
        }
        return (
            <AppBar
                title={this.props.title}
                onLeftIconButtonTouchTap={this.leftTap}
                iconElementLeft={leftElement}
                iconElementRight={rightElement} />
        );
    }
});

export default Toolbar;