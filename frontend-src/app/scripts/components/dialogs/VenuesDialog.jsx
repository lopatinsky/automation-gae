import React from 'react';
import { Dialog} from 'material-ui';
import { List, ListItem, ListDivider } from 'material-ui';
import { VenuesStore } from '../../stores';

const VenuesDialog = React.createClass({
    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
            return (
                <div>
                    <ListItem
                        onClick={() => this.dismiss(venue)}>
                        <div>
                            <div style={{fontSize: '14px', lineHeight: '120%'}}><b>{venue.title}</b></div>
                            <div style={{padding: '4px 0 0 0', fontSize: '14px', lineHeight: '120%'}}>{venue.address}</div>
                            <div style={{padding: '4px 0 0 0', fontSize: '14px', lineHeight: '120%'}}>{venue.schedule_str}</div>
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
                contentStyle={{width: '90%'}}
                bodyStyle={{padding: '12px', overflowY: 'auto', maxHeight: '487px'}}
                autoScrollBodyContent={true}
                ref="venuesDialog">
                <List>
                    {this._getVenues()}
                </List>
            </Dialog>
        );
    }
});

export default VenuesDialog;