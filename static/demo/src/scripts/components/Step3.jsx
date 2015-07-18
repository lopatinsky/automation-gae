import React from 'react';
import { Button } from 'react-bootstrap';
import { Navigation } from 'react-router';
import assign from 'object-assign';
import InputGroup from './InputGroup';
import VenueStore from '../stores/VenueStore';
import { required } from '../validators';
import AddressPicker from './AddressPicker';
import Actions from '../Actions';

const Step3 = React.createClass({
    mixins: [Navigation],
    titleValidators: [required('Введите название заведения')],
    getInitialState() {
        return assign({
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
            <h2>Введите информацию о заведении</h2>
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
                <div style={{textAlign: 'right'}}>
                    <Button onClick={this._onNextClick} bsStyle="primary">Далее</Button>
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
    _onNextClick() {
        let valid = this.refs.title.validate(true) & !!this.state.address;
        if (valid) {
            this.transitionTo('finish');
        }
        if (!this.state.address) {
            this._setAddressValid(false);
        }
    }
});
export default Step3;
