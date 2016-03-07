import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { OrderStore } from '../../stores';

const TimeSlotsDialog = React.createClass({
    getInitialState() {
        return {
            open: false,
            slots: OrderStore.chosenDeliveryType ? OrderStore.chosenDeliveryType.slots : [],
            chosenSlot: OrderStore.slotId
        };
    },

    _onOrderStoreChange() {
        this.setState({
            slots: OrderStore.chosenDeliveryType ? OrderStore.chosenDeliveryType.slots : [],
            chosenSlot: OrderStore.slotId
        });
    },

    componentDidMount() {
        OrderStore.addChangeListener(this._onOrderStoreChange);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._onOrderStoreChange);
    },

    _getSlots() {
        if (!this.state.slots) {
            return null;
        }
        const result = [];
        for (let slot of this.state.slots) {
            result.push(
                <ListItem key={slot.id}
                          primaryText={slot.name}
                          onTouchTap={() => this.dismiss(slot)}/>
            );
            result.push(<Divider key={`divider_${slot.id}`}/>);
        }
        result.pop();
        return result;
    },

    show() {
        this.setState({
            open: true
        });
    },

    dismiss(slot) {
        this.props.onSlotChosen(slot.id);
        this.setState({
            open: false
        })
    },

    render() {
        return (
            <Dialog
                bodyStyle={{padding: '12px'}}
                autoScrollBodyContent={true}
                open={this.state.open}
                onRequestClose={() => this.setState({open: false})}
                ref="timeSlotsDialog">
                <List>
                    {this._getSlots()}
                </List>
            </Dialog>
        );
    }
});

export default TimeSlotsDialog;