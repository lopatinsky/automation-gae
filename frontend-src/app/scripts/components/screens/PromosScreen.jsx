import React from 'react';
import { Card, CardText, CardMedia } from 'material-ui';
import { PromosStore } from '../../stores';
import { ServerRequests } from '../../actions';

const PromosScreen = React.createClass({
    _refresh() {
        this.setState({});
    },

    getPromos() {
        var promos = PromosStore.getPromos();
        return promos.map(promo => {
            var picCard = <div style={{display: 'table-cell', width: '25%', padding: '0 12px 12px 12px'}}>
                <CardMedia>
                    <img src={promo.icon}/>
                </CardMedia>
            </div>;
            if (promo.icon == null || promo.icon == '') {
                picCard = <div/>;
            }
            var descriptionCard = <div style={{height: '64px', overflow: 'hidden'}}>
                {promo.description}
            </div>;
            if (promo.description == '') {
                descriptionCard = <div/>;
            }
            return <Card style={{margin: '0 12px 12px 12px'}}>
                {picCard}
                <div style={{display: 'table-cell', padding: '12px 0 0 12px'}}>
                    <div>
                        <b>{promo.title}</b>
                    </div>
                    {descriptionCard}
                </div>
            </Card>;
        });
    },

    componentDidMount() {
        ServerRequests.loadPromos();
        PromosStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        PromosStore.removeChangeListener(this._refresh);
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this.getPromos()}
        </div>;
    }
});

export default PromosScreen;