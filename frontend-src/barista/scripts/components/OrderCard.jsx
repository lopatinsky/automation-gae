import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import FlatButton from 'material-ui/lib/flat-button';
import AutoPrefix from 'material-ui/lib/styles/auto-prefix';
import { AjaxStore, OrderStore, ConfigStore } from '../stores';
import { SpinnerWrap, OrderInfo } from '../components';

const OrderCard = React.createClass({
    getInitialState() {
        return {
            sendingRequest: false,
            handle: {
                cancel: this._handleAction.bind(this, 'Cancel'),
                postpone: this._handleAction.bind(this, 'Postpone'),
                confirm: this._handleAction.bind(this, 'Confirm'),
                done: this._handleAction.bind(this, 'Done'),
                move: this._handleAction.bind(this, 'Move'),
                sync: this._handleAction.bind(this, 'Sync')
            }
        };
    },
    componentDidMount() {
        AjaxStore.addChangeListener(this._onAjaxStoreChange);
    },
    componentWillUnmount() {
        AjaxStore.removeChangeListener(this._onAjaxStoreChange);
    },
    _onAjaxStoreChange() {
        this.setState({
            sendingRequest: AjaxStore.sending[`order_action_${this.props.order.id}`]
        });
    },
    _handleAction(action) { // action -- eg Done, Cancel, etc
        const methodName = 'onTouchTap' + action;
        this.props[methodName] ?
            this.props[methodName](this.props.order) :
            console.log(`missing handler for action ${action}`);
    },
    _renderActions() {
        const style = {borderTop: '1px solid #ccc', textAlign: 'right', padding: 8};
        if (this.props.appKind == ConfigStore.APP_KIND.AUTO_APP) {
            let order = this.props.order,
                primaryActionLabel, primaryActionHandler;
            if (order.deliveryType == OrderStore.DELIVERY_TYPE.DELIVERY && order.status == OrderStore.STATUS.NEW) {
                primaryActionLabel = 'Подтвердить';
                primaryActionHandler = this.state.handle.confirm;
            } else {
                primaryActionLabel = 'Выдать';
                primaryActionHandler = this.state.handle.done;
            }
            return <div style={style}>
                <FlatButton label='Отменить' onTouchTap={this.state.handle.cancel} disabled={this.state.sendingRequest}/>
                <FlatButton label='Сменить точку' onTouchTap={this.state.handle.move} disabled={this.state.sendingRequest}/>
                <FlatButton label='Перенести' onTouchTap={this.state.handle.postpone} disabled={this.state.sendingRequest}/>
                <FlatButton label={primaryActionLabel} onTouchTap={primaryActionHandler} disabled={this.state.sendingRequest} secondary={true}/>
            </div>;
        } else if (this.props.appKind == ConfigStore.APP_KIND.RESTO_APP) {
            return <div style={style}>
                <FlatButton label='Обновить статус' onTouchTap={this.state.handle.sync} disabled={this.state.sendingRequest} secondary={true}/>
            </div>
        } else return null;
    },
    render() {
        let contentStyle = AutoPrefix.all({
            transition: "background-color 0.2s ease-in-out",
            backgroundColor: this.props.highlightColor
        });
        return <Card style={{margin:'0 12px 12px', fontWeight: 300}}>
            <SpinnerWrap show={this.state.sendingRequest}>
                <CardText style={contentStyle}>
                    <OrderInfo order={this.props.order}
                               highlightColor={this.props.highlightColor}/>
                </CardText>
                {this._renderActions()}
            </SpinnerWrap>
        </Card>
    }
});
export default OrderCard;
