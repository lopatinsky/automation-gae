import React from 'react';
import { VenuesStore } from '../../stores';
import { Card, CardText } from 'material-ui';

const VenuesScreen = React.createClass({
    _refresh() {
        this.setState({});
    },

    _getVenues() {
        var venues = VenuesStore.getVenues();
        return venues.map(venue => {
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
        VenuesStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        VenuesStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this._getVenues()}
        </div>;
    }
});

export default VenuesScreen;