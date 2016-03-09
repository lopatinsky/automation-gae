import React from 'react';
import Paper from 'material-ui/lib/paper';
import FlatButton from 'material-ui/lib/flat-button';
import { MenuStore } from '../stores';

const MenuCategory = React.createClass({
    contextTypes: {
        router: React.PropTypes.object.isRequired,
    },

    _onMenuCategoryTap() {
        this.context.router.push(`/menu/${this.props.category.info.category_id}`);
    },

    render() {
        var category = this.props.category;
        const picCardStyle = {
            backgroundImage: `url(${category.info.pic})`,
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
            backgroundSize: 'contain',
            width: 140,
            flexShrink: 0
        },
            picCard = <div style={picCardStyle}/>;
        const content = <div style={{padding: 12, flexGrow: 1, alignSelf: 'center'}}>
            {category.info.title}
        </div>;
        return <Paper style={{margin:'0 12px 12px', display: 'flex', minHeight: 105}}
                      onTouchTap={this._onMenuCategoryTap}>
            {picCard}
            {content}
        </Paper>;
    }
});

export default MenuCategory;