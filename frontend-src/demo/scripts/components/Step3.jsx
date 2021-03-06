import React from 'react';
import { Button } from 'react-bootstrap';
import InputGroup from './InputGroup';
import VenueStore from '../stores/VenueStore';
import ProgressStore from '../stores/ProgressStore';
import { required } from '../validators';
import AddressPicker from './AddressPicker';
import Actions from '../Actions';

const Step3 = React.createClass({
    titleValidators: [required('Введите название заведения')],
    getInitialState() {
        return Object.assign({
            choosingAddress: false,
            addressBsStyle: null,
            addressHelp: null
        }, VenueStore.getVenueInfo());
    },
    _onStoreChange() {
        this.setState(VenueStore.getVenueInfo());
    },
    componentDidMount() {
        VenueStore.addChangeListener(this._onStoreChange);
    },
    componentWillUnmount() {
        VenueStore.removeChangeListener(this._onStoreChange);
    },
    render() {
        let addressButton = this.state.choosingAddress ?
            <Button onClick={this._cancelAddress}>Отмена</Button> :
            <Button onClick={this._selectAddress}>Выбрать</Button>;
        let mapPart = this.state.choosingAddress ? <AddressPicker onPicked={this._onAddressPicked}/>: null;
        return <div>
            <h3>Введите информацию о заведении</h3>
            <div className="cards-container">
                <div className="card">
                    <div>
                        <InputGroup ref='title'
                                    type='text'
                                    value={this.state.title}
                                    placeholder='Кафе на Тверской'
                                    label='Название заведения'
                                    onChange={this._onInputChange}
                                    validators={this.titleValidators}/>
                        <InputGroup ref='address'
                                    type='text'
                                    value={this.state.address}
                                    placeholder='Москва, Тверская ул., 1'
                                    label='Адрес'
                                    readOnly
                                    buttonBefore={addressButton}
                                    noValidation
                                    bsStyle={this.state.addressBsStyle}
                                    help={this.state.addressHelp}/>
                        {mapPart}
                    </div>
                </div>
                <div>
                    <Button onClick={this._onPrevClick}>Назад</Button>
                    <Button bsStyle='primary' onClick={this._onNextClick} className="pull-right">Далее</Button>
                </div>
            </div>
        </div>;
    },
    _onInputChange() {
        Actions.updateVenueTitle(this.refs.title.getValue());
    },
    _selectAddress() {
        this.setState({choosingAddress: true})
    },
    _cancelAddress() {
        this.setState({choosingAddress: false})
    },
    _onAddressPicked({lat, lng, address}) {
        this.setState({choosingAddress: false});
        this._setAddressValid(true);
        Actions.updateVenueLocation({lat, lng, address});
    },
    _setAddressValid(valid) {
        if (valid) {
            this.setState({addressBsStyle: 'success', addressHelp: null});
        } else {
            this.setState({addressBsStyle: 'error', addressHelp: 'Выберите адрес заведения'});
        }
    },
    _onPrevClick() {
        Actions.goToStep(ProgressStore.steps.MENU);
    },
    _onNextClick() {
        let valid = this.refs.title.validate(true) & !!this.state.address;
        if (valid) {
            Actions.postToServer();
        }
        if (!this.state.address) {
            this._setAddressValid(false);
        }
    }
});
export default Step3;
