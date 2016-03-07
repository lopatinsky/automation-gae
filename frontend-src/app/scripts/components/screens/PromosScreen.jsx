import React from 'react';
import Paper from 'material-ui/lib/paper';
import { PromosStore } from '../../stores';
import { ServerRequests } from '../../actions';

const PromosScreen = React.createClass({
    getInitialState() {
        return {
            promos: PromosStore.promos
        };
    },

    _onPromosStoreChanged() {
        this.setState({
            promos: PromosStore.promos
        });
    },

    componentDidMount() {
        PromosStore.addChangeListener(this._onPromosStoreChanged);
    },

    componentWillUnmount() {
        PromosStore.removeChangeListener(this._onPromosStoreChanged);
    },

    getPromos() {
        if (this.state.promos.length == 0) {
            return <div style={{textAlign: 'center'}}>
                Нет подходящих акций
            </div>;
        }
        return this.state.promos.map(promo => {
            let picCard = null;
            if (promo.icon) {
                const picCardStyle = {
                    backgroundImage: `url(${promo.icon})`,
                    backgroundRepeat: 'no-repeat',
                    backgroundPosition: 'center',
                    backgroundSize: 'contain',
                    width: 76,
                    flexShrink: 0,
                    margin: 12
                };
                picCard = <div style={picCardStyle}></div>;
            }
            const content = <div style={{padding: 12, flexGrow: 1}}>
                <div style={{marginBottom: 4}}>{promo.title}</div>
                {promo.description && <div style={{fontSize: 12, marginBottom: 4}}>{promo.description}</div>}
            </div>;
            const minHeight = picCard ? 100 : null;
            return <Paper key={promo.id}
                          style={{margin:'0 12px 12px', display: 'flex', minHeight}}>
                {picCard}
                {content}
            </Paper>;
        });
    },

    render() {
        return <div style={{padding: '76px 0 0 0'}}>
            {this.getPromos()}
        </div>;
    }
});

export default PromosScreen;
