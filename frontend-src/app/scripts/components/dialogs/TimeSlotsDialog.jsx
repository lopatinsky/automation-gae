import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { OrderStore, VenuesStore } from '../../stores';

const TimeSlotsDialog = React.createClass({
    getInitialState() {
        return {
            open: false
        };
    },

    _getSlots() {
        var delivery = VenuesStore.getChosenDelivery();
        if (!delivery) {
            return null;
        }
        const result = [];
        for (let slot of delivery.slots) {
            result.push(
                <ListItem key={slot.id}
                          primaryText={slot.name}
                          onClick={() => this.dismiss(slot)}/>
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
        OrderStore.setSlotId(slot.id);
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
                ref="timeSlotsDialog">
                <List>
                    {this._getSlots()}
                </List>
            </Dialog>
        );
    }
});

export default TimeSlotsDialog;