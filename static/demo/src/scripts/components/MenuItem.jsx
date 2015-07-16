import React from 'react';
import { Button, Glyphicon, Label } from 'react-bootstrap';
import MenuStore from '../stores/MenuStore';
import Actions from '../Actions';
import InputGroup from './InputGroup';
import { required, pattern, min } from '../validators';

const MenuItem = React.createClass({
    titleValidators: [required("Введите название продукта")],
    priceValidators: [required("Введите цену продукта"), min(0, "Введите положительную цену")],
    imageValidators: [pattern(/^https?:\/\/[a-z0-9-.]+\//i, "Введите корректную ссылку")],
    defaultImageUrl: 'http://placehold.it/100x50/eeeeee/777777?text=Нет',
    componentWillMount() {
        if (this.props.edit && this.props.edit.item == this.props.item.id) {
            this.setState(this.props.item);
        }
    },
    render() {
        if (this.props.edit && this.props.edit.item == this.props.item.id) {
            return <div className='form-horizontal menu-item'>
                <InputGroup ref='title'
                            type='text'
                            value={this.state.title}
                            placeholder='Холодный чай'
                            label='Название продукта'
                            validators={this.titleValidators}
                            onChange={this._onEditInputChange}/>
                <InputGroup ref='description'
                            type='textarea'
                            value={this.state.description}
                            placeholder='Самый вкусный холодный чай на планете!'
                            label='Описание продукта'
                            onChange={this._onEditInputChange}/>
                <InputGroup ref='price'
                            type='number'
                            value={this.state.price}
                            placeholder='100'
                            label='Цена'
                            validators={this.priceValidators}
                            onChange={this._onEditInputChange}/>
                <InputGroup ref='imageUrl'
                            type='text'
                            value={this.state.imageUrl}
                            placeholder='http://example.com/image.png'
                            label='Ссылка на изображение'
                            validators={this.imageValidators}
                            onChange={this._onEditInputChange}/>
                <InputGroup>
                    <Button bsStyle='primary' onClick={this._finishEdit}>
                        <Glyphicon glyph='ok'/> Сохранить
                    </Button>&nbsp;
                    <Button onClick={this._cancelEdit}>
                        <Glyphicon glyph='remove'/> Отмена
                    </Button>
                </InputGroup>
            </div>;
        } else {
            return <div className="menu-item clearfix">
                <img src={this.props.item.imageUrl || this.defaultImageUrl} className='menu-item-image'/>
                <div className='menu-item-info'>
                    <div className="pull-right">
                        <Button bsSize='small' onClick={this._edit} disabled={this.props.edit !== null}>
                            <Glyphicon glyph='pencil'/>
                        </Button>
                    </div>
                    <h4>
                        {this.props.item.title}&nbsp;
                        <Label bsStyle='primary'>{this.props.item.price} руб.</Label>
                    </h4>
                    <p>{this.props.item.description}</p>
                </div>
            </div>;
        }
    },

    _edit() {
        this.setState(this.props.item);
        Actions.startEditItem(this.props.item.id);
    },
    _finishEdit() {
        let valid = this.refs.title.validate(true) &
                this.refs.description.validate(true) &
                this.refs.price.validate(true) &
                this.refs.imageUrl.validate(true);
        if (valid) {
            Actions.finishEditItem(this.state);
        }
    },
    _cancelEdit() {
        Actions.cancelEdit();
    },
    _onEditInputChange() {
        let newState = {};
        for (var prop of ['title', 'description', 'price', 'imageUrl']) {
            newState[prop] = this.refs[prop].getValue();
        }
        this.setState(newState);
    }
});
export default MenuItem;
