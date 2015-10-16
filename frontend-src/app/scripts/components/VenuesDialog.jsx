import React from 'react';
import { Dialog} from 'material-ui';
import { List, ListItem, ListDivider } from 'material-ui';
import { VenuesStore } from '../stores';

const VenuesDialog = React.createClass({
    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
            return (
                <div>
                    <ListItem
                        onClick={() => this.dismiss(venue)}>
                        <div>
                            <div><b>{venue.title}</b></div>
                            <div style={{padding: '6px 0 0 0'}}>{venue.address}</div>
                            <div style={{padding: '6px 0 0 0'}}>{venue.schedule_str}</div>
                        </div>
                    </ListItem>
                    <ListDivider/>
                </div>
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
            <Dialog
                autoScrollBodyContent="true"
                ref="venuesDialog">
                <List>
                    {this._getVenues()}
                </List>
            </Dialog>
        );
    }
});

export default VenuesDialog;