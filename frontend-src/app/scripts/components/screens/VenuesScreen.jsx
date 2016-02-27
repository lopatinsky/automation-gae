import React from 'react';
import { VenuesStore } from '../../stores';
import { Card, CardText } from 'material-ui';

const VenuesScreen = React.createClass({
    getInitialState() {
        return {
            venues: VenuesStore.venues
        }
    },

    _onVenuesStoreChanged() {
        this.setState({
            venues: VenuesStore.venues
        })
    },

    _getVenues() {
        return this.state.venues.map(venue => {
            return (
                <Card key={venue.id} style={{margin: '0 12px 12px 12px'}}>
                    <div style={{padding: '12px 12px 0 12px', lineHeight: '120%'}}>
                        <b>{venue.title}</b>
                    </div>
                    <div style={{padding: '6px 12px 0 12px', lineHeight: '120%'}}>
                        {venue.address}
                    </div>
                    <div style={{padding: '6px 12px 12px 12px', lineHeight: '120%'}}>
                        {venue.schedule_str}
                    </div>
                </Card>
            );
        });
    },

    componentDidMount() {
        VenuesStore.addChangeListener(this._onVenuesStoreChanged);
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._onVenuesStoreChanged);
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this._getVenues()}
        </div>;
    }
});

export default VenuesScreen;