import React from 'react';
import { VenuesStore } from '../stores';
import { Card, CardText } from 'material-ui';

const VenuesScreen = React.createClass({
    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
            return (
                <Card style={{margin: '0 12px 12px 12px'}}>
                    <div style={{padding: '12px 0 0 12px'}}>
                        <b>{venue.title}</b>
                    </div>
                    <div style={{padding: '6px 0 0 12px'}}>
                        {venue.address}
                    </div>
                    <div style={{padding: '6px 0 12px 12px'}}>
                        Пн-вс: 10:00 - 11:00
                    </div>
                </Card>
            );
        });
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this._getVenues()}
        </div>;
    }
});

export default VenuesScreen;