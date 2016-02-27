import React from 'react';
import { Dialog, List, ListItem, Divider } from 'material-ui';
import { VenuesStore } from '../../stores';
import { AppActions } from '../../actions';

const VenuesDialog = React.createClass({
    getInitialState() {
        return {
            venues: VenuesStore.venues,
            open: false
        };
    },

    _onVenuesStoreChange() {
        this.setState({
            venues: VenuesStore.venues
        });
    },

    componentDidMount() {
        VenuesStore.addChangeListener(this._onVenuesStoreChange);
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._onVenuesStoreChange)
    },

    _getVenues() {
        const result = [];
        for (let venue of this.state.venues) {
            result.push(
                <ListItem key={venue.id} onTouchTap={() => this.dismiss(venue)}>
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
        AppActions.setVenue(venue);
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