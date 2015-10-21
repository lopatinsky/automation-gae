import React from 'react';
import { Dialog, List, ListItem, ListDivider } from 'material-ui';
import { OrderStore, VenuesStore } from '../../stores';

const TimeSlotsDialog = React.createClass({
    _getSlots() {
        var delivery = VenuesStore.getChosenDelivery();
        return delivery.slots.map(slot => {
            return (
                <div>
                    <ListItem
                        primaryText={slot.name}
                        onClick={() => this.dismiss(slot)}/>
                    <ListDivider/>
                </div>
            );
        });
    },

    show() {
        this.refs.timeSlotsDialog.show();
    },

    dismiss(slot) {
        OrderStore.setSlotId(slot.id);
        this.refs.timeSlotsDialog.dismiss();
    },

    render() {
        return (
            <Dialog
                autoScrollBodyContent="true"
                ref="timeSlotsDialog">
                <List>
                    {this._getSlots()}
                </List>
            </Dialog>
        );
    }
});

export default TimeSlotsDialog;