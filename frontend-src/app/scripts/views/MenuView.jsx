import React from 'react';
import { Toolbar, MenuScreen } from '../components'
import Actions from '../Actions';

const MenuView = React.createClass({
    componentDidMount() {
        Actions.loadMenu();
    },

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