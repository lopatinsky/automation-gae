import React from 'react';
import { AppBar, IconButton, FlatButton, Icons, FontIcon } from 'material-ui';
import Router from 'react-router';
import { Navigation } from 'react-router';
import { OrderStore, MenuStore } from '../stores';
import Colors from 'material-ui/lib/styles/colors';

const Toolbar = React.createClass({
    ORDER_BUTTON: 'order',

    mixins: [Navigation, Router.State],

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
        MenuStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._refresh);
        MenuStore.removeChangeListener(this._refresh);
    },

    render() {
        var rightElement;
        if (this.props.right == this.ORDER_BUTTON) {
            var label = OrderStore.getTotalSum() + " руб.";
            rightElement = <FlatButton
                onClick={this.rightTap}>
                <div style={{display: 'table'}}>
                    <div style={{display: 'table-cell', padding: '0 6px 0 6px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                                  color={Colors.white}
                                  className="material-icons">
                            shopping_basket
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell'}}>
                        {label}
                    </div>
                </div>
            </FlatButton>;
        }
        var leftElement;
        var nestedCategory = false;
        if (this.getPathname() == '/' && MenuStore.canUndoCategories()) {
            nestedCategory = true;
        }
        if (this.props.back == true || nestedCategory) {
            leftElement = <IconButton onClick={this.leftTap}>
                <Icons.NavigationChevronLeft/>
            </IconButton>;
        }
        return (
            <AppBar
                style={{position: 'fixed', height: '64px'}}
                title={this.props.title}
                onLeftIconButtonTouchTap={this.leftTap}
                iconElementLeft={leftElement}
                iconElementRight={rightElement} />
        );
    }
});

export default Toolbar;