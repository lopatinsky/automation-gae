import React from 'react';
import { Toolbar } from '../components';
import { MenuScreen } from '../components/screens';

const MenuView = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    toolbarLeftTap() {
        if (this.props.params.category_id) {
            this.context.router.goBack();
        } else {
            this.props.getDrawer().toggle();
        }
    },
    render() {
        return (
            <div>
                <Toolbar
                    title='Меню'
                    view={this}
                    back={!!this.props.params.category_id}
                    right='order'/>
                <MenuScreen category={this.props.params.category_id} />
            </div>
        );
    }
});
export default MenuView;