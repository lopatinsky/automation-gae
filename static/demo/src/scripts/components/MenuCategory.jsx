import React from 'react';
import { Button, Glyphicon } from 'react-bootstrap';
import MenuItem from './MenuItem';
import Actions from '../Actions';

const MenuCategory = React.createClass({
    render() {
        let items = this.props.category.items.map(item => {
            return <MenuItem key={item.id} item={item} edit={this.props.edit}/>
        });
        return <div className='menu-category card'>
            <h2>{this.props.category.title}</h2>
            {items}
            <div>
                <Button onClick={this._add} disabled={this.props.edit !== null}>
                    <Glyphicon glyph='plus'/> Добавить продукт
                </Button>
            </div>
        </div>
    },
    _add() {
        Actions.addItem(this.props.category.id);
    }
});
export default MenuCategory;
