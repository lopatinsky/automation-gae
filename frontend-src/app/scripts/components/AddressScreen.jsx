import React from 'react';
import { DropDownMenu, TextField } from 'material-ui';
import { AddressStore } from '../stores';
import Actions from '../Actions';

const AddressScreen = React.createClass({
     _refresh() {
        this.setState({
            street: this.refs.street.getValue(),
            home: this.refs.home.getValue(),
            flat: this.refs.flat.getValue()
        });
    },

    _onCityTap(e, selectedIndex, menuItem) {
        AddressStore.setChosenCity(menuItem.id);
    },

    saveAddress() {
        AddressStore.setAddress(this.refs.street.getValue(), this.refs.home.getValue(), this.refs.flat.getValue());
    },

    getInitialState() {
        return {
            street: AddressStore.getStreet(),
            home: AddressStore.getHome(),
            flat: AddressStore.getFlat()
        }
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
                <TextField hintText="Улица" ref="street" value={this.state.street} onChange={this._refresh}/>
                <TextField hintText="Дом" ref="home" value={this.state.home} onChange={this._refresh}/>
                <TextField hintText="Квартира" ref="flat" value={this.state.flat} onChange={this._refresh}/>
            </div>
        </div>;
    }
});

export default AddressScreen;