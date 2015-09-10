import React from 'react';
import { Toolbar, MenuScreen } from '../components'

const MenuView = React.createClass({
    render() {
        return (
            <div>
                <Toolbar title='Меню' />
                <MenuScreen />
            </div>
        );
    }
});
export default MenuView;