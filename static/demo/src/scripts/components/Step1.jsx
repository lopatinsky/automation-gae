import React from 'react';
import { ButtonLink } from 'react-router-bootstrap';
import Input from './Input'
import InfoStore from '../stores/InfoStore';
import Actions from '../Actions';

const Step1 = React.createClass({
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
        console.log(name, phone, email);
        Actions.updateInfo(name, phone, email);
    },
    render() {
        console.log('rendering', this.state);
        return <div>
            <h4>Введите информацию о Вашей компании</h4>
            <form className='form-horizontal'>
                <Input ref='name'
                       type='text'
                       value={this.state.name}
                       label='Название компании'
                       required
                       onChange={this._onInputChange}/>
                <Input ref='phone'
                       type='text'
                       value={this.state.phone}
                       label='Ваш телефон'
                       addonBefore={<span>+7</span>}
                       onChange={this._onInputChange}/>
                <Input ref='email'
                       type='email'
                       value={this.state.email}
                       label='Ваш e-mail'
                       onChange={this._onInputChange}/>
                <Input>
                    <ButtonLink to='step2'>Далее</ButtonLink>
                </Input>
            </form>
        </div>;
    }
});
export default Step1;
