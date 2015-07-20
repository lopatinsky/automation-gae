import React from 'react';
import { Button, Glyphicon } from 'react-bootstrap';
import MenuItem from './MenuItem';
import Actions from '../Actions';
import InputGroup from './InputGroup';
import { required } from '../validators';

const MenuCategory = React.createClass({
    titleValidators: [required("Введите название категории")],
    componentWillMount() {
        if (this.props.edit && this.props.edit.category == this.props.category.id) {
            this.setState(this.props.category);
        }
    },
    render() {
        let headingPart;
        if (this.props.edit && this.props.edit.category == this.props.category.id) {
            headingPart = <div>
                <div>
                    <InputGroup ref='title'
                                type='text'
                                value={this.state.title}
                                placeholder='Напитки'
                                label='Название категории'
                                validators={this.titleValidators}
                                onChange={this._onEditInputChange}/>
                    <InputGroup>
                        <Button bsStyle='primary' onClick={this._finishEdit}>
                            <Glyphicon glyph='ok'/> Сохранить
                        </Button>&nbsp;
                        <Button onClick={this._cancelEdit}>
                            <Glyphicon glyph='remove'/> Отмена
                        </Button>
                    </InputGroup>
                </div>
            </div>;
        } else {
            headingPart =
                <h4>
                    {this.props.category.title}&nbsp;
                    <Button bsSize='small' onClick={this._edit} disabled={this.props.edit !== null}>
                        <Glyphicon glyph='pencil'/>
                    </Button>
                </h4>;
        }

        let items = this.props.category.items.map(item => {
            return <MenuItem key={item.id} item={item} edit={this.props.edit}/>
        });

        let hideAddPart = this.props.category._new ||
            this.props.category.items.length && this.props.category.items[this.props.category.items.length - 1]._new;
        let addPart = hideAddPart ? null :
            <div>
                <Button onClick={this._add} disabled={this.props.edit !== null}>
                    <Glyphicon glyph='plus'/> Добавить продукт
                </Button>
            </div>;
        return <div className='menu-category card'>
            {headingPart}
            {items}
            {addPart}
        </div>
    },
    _edit() {
        this.setState(this.props.category);
        Actions.startEditCategory(this.props.category.id);
    },
    _finishEdit() {
        Actions.finishEditCategory(this.state);
    },
    _cancelEdit() {
        Actions.cancelEdit();
    },
    _add() {
        Actions.addItem(this.props.category.id);
    },
    _onEditInputChange() {
        this.setState({
            title: this.refs.title.getValue()
        });
    }
});
export default MenuCategory;
