import React from 'react';
import { Dialog} from 'material-ui';
import { List, ListItem, Divider } from 'material-ui';
import { VenuesStore } from '../../stores';

const VenuesDialog = React.createClass({
    getInitialState() {
        return {
            open: false
        };
    },

    _getVenues() {
        var venues = VenuesStore.getVenues();
        const result = [];
        for (let venue of venues) {
            result.push(
                <ListItem key={venue.id} onClick={() => this.dismiss(venue)}>
                    <div>
                        <div style={{fontSize: '14px', lineHeight: '120%'}}><b>{venue.title}</b></div>
                        <div style={{padding: '4px 0 0 0', fontSize: '14px', lineHeight: '120%'}}>{venue.address}</div>
                        <div style={{padding: '4px 0 0 0', fontSize: '14px', lineHeight: '120%'}}>{venue.schedule_str}</div>
                    </div>
                </ListItem>
            );
            result.push(<Divider key={`divider_${venue.id}`}/>);
        }
        result.pop();
        return result;
    },

    show() {
        this.setState({
            open: true
        });
    },

    dismiss(venue) {
        VenuesStore.setChosenVenue(venue);
        this.setState({
            open: false
        });
    },

    render() {
        return (
            <Dialog
                contentStyle={{width: '90%'}}
                bodyStyle={{padding: '12px', overflowY: 'auto', maxHeight: '487px'}}
                autoScrollBodyContent={true}
                open={this.state.open}
                ref="venuesDialog">
                <List>
                    {this._getVenues()}
                </List>
            </Dialog>
        );
    }
});

export default VenuesDialog;