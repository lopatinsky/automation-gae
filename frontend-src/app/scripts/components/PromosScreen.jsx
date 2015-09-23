import React from 'react';
import { Card, CardText } from 'material-ui';
import { PromosStore } from '../stores';
import Actions from '../Actions';

const PromosScreen = React.createClass({
    getPromos() {
        var promos = PromosStore.getPromos();
        return promos.map(promo => {
            return <Card>
                <CardText>
                    {promo.title}
                </CardText>
            </Card>;
        });
    },

    componentDidMount() {
        Actions.loadPromos();
        PromosStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        PromosStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div>
            {this.getPromos()}
        </div>;
    }
});

export default PromosScreen;