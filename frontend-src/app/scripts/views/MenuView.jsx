import React from 'react';
import { Toolbar, MenuScreen } from '../components'

const MenuView = React.createClass({

    render() {
        return (
            <div>
                <Toolbar title="Menu" />
                <MenuScreen />
            </div>
        );
    }
});
export default MenuView;