import React from 'react';
import { Dialog, List, ListItem, ListDivider } from 'material-ui';
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
            return <div/>;
        }
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