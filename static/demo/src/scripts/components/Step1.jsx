import React from 'react';
import { Button } from 'react-bootstrap';
import { Navigation } from 'react-router';
import Input from './InputGroup'
import InfoStore from '../stores/InfoStore';
import Actions from '../Actions';
import { required, pattern, email } from '../validators';

const Step1 = React.createClass({
    mixins: [Navigation],
    nameValidators: [required("Введите название компании")],
    phoneValidators: [
        required("Введите Ваш номер телефона"),
        pattern(/^\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2}\D*$/, "Введите корректный номер телефона")
    ],
    emailValidators: [required("Введите Ваш email-адрес"), email("Введите корректный email-адрес")],

    _onStoreChange() {
        this.setState(InfoStore.getMainInfo());
    },
    componentDidMount() {
        InfoStore.addChangeListener(this._onStoreChange);
    },
    componentWillUnmount() {
        InfoStore.removeChangeListener(this._onStoreChange);
    },
    getInitialState() {
        return InfoStore.getMainInfo();
    },

    _onInputChange() {
        let name = this.refs.name.getValue(),
            phone = this.refs.phone.getValue(),
            email = this.refs.email.getValue();
        Actions.updateInfo(name, phone, email);
    },
    _onNextClick() {
        let valid = this.refs.name.validate(true) &
            this.refs.phone.validate(true) &
            this.refs.email.validate(true);
        if (valid) {
            this.transitionTo('step2');
        }
    },
    render() {
        return <div>
            <h2>Введите информацию о Вашей компании</h2>
            <form className='form-horizontal'>
                <Input ref='name'
                       type='text'
                       value={this.state.name}
                       placeholder='Кафе "У Ивана"'
                       label='Название компании'
                       onChange={this._onInputChange}
                       validators={this.nameValidators}/>
                <Input ref='phone'
                       type='text'
                       value={this.state.phone}
                       placeholder='999 000-00-00'
                       label='Ваш телефон'
                       addonBefore={<span>+7</span>}
                       onChange={this._onInputChange}
                       validators={this.phoneValidators}/>
                <Input ref='email'
                       type='email'
                       value={this.state.email}
                       placeholder='name@example.com'
                       label='Ваш e-mail'
                       onChange={this._onInputChange}
                       validators={this.emailValidators}/>
                <Input>
                    <Button onClick={this._onNextClick}>Далее</Button>
                </Input>
            </form>
        </div>;
    }
});
export default Step1;
