import React from 'react';
import { VenuesStore } from '../stores';
import { Card, CardText } from 'material-ui';

const VenuesScreen = React.createClass({
    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
            return (
                <Card>
                    <CardText>
                        {venue.title}
                    </CardText>
                </Card>
            );
        });
    },

    render() {
        return <div>
            {this._getVenues()}
        </div>;
    }
});

export default VenuesScreen;