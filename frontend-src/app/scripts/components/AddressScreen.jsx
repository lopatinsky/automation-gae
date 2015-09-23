import React from 'react';
import { DropDownMenu, TextField } from 'material-ui';
import { AddressStore } from '../stores';
import Actions from '../Actions';

const AddressScreen = React.createClass({
     _refresh() {
        this.setState({});
    },

    _onCityTap(e, selectedIndex, menuItem) {
        AddressStore.setChosenCity(menuItem.id);
    },

    _setAddress() {
        AddressStore.setAddress(this.refs.street.getValue(), this.refs.home.getValue(), this.refs.flat.getValue());
    },

    componentDidMount() {
        AddressStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        AddressStore.removeChangeListener(this._refresh);
    },

    render() {
        var cities = AddressStore.getCities().map(city => {
                return {
                    text: city,
                    id: city
                }
            }
        );
        return <div>
            <div>
                <DropDownMenu
                    menuItems={cities}
                    selectedIndex={AddressStore.getCityIndex(AddressStore.getChosenCity())}
                    onChange={this._onCityTap}/>
            </div>
            <div>
                <TextField hintText="Улица" ref="street" value={AddressStore.getStreet()} onChange={this._setAddress}/>
                <TextField hintText="Дом" ref="home" value={AddressStore.getHome()} onChange={this._setAddress}/>
                <TextField hintText="Квартира" ref="flat" value={AddressStore.getFlat()} onChange={this._setAddress}/>
            </div>
        </div>;
    }
});

export default AddressScreen;