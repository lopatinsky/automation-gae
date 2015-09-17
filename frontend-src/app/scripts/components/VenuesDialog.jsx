import React from 'react';
import { Dialog} from 'material-ui';
import { List, ListItem } from 'material-ui';
import { VenuesStore } from '../stores';

const VenuesDialog = React.createClass({
    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
            return (
                <ListItem
                    primaryText={venue.title}
                    secondaryText={venue.address}
                    onClick={() => this.dismiss(venue)}/>
            );
        });
    },

    show() {
        this.refs.venuesDialog.show();
    },

    dismiss(venue) {
        VenuesStore.setChosenVenue(venue);
        this.refs.venuesDialog.dismiss();
    },

    render() {
        return (
            <Dialog ref="venuesDialog">
                <List>
                    {this._getVenues()}
                </List>
            </Dialog>
        );
    }
});

export default VenuesDialog;