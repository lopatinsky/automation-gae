import React from 'react';
import { DropDownMenu, TextField, Paper, Card } from 'material-ui';
import { AddressStore } from '../../stores';

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
        return <div style={{padding: '76px 0 0 0'}}>
            <div style={{width: '100%'}}>
                <Paper style={{margin: '0 12px 0 12px', zIndex: '9'}}>
                    <DropDownMenu
                        style={{zIndex: '10', width: '100%'}}
                        underlineStyle={{display: 'none'}}
                        menuItems={cities}
                        selectedIndex={AddressStore.getCityIndex(AddressStore.getChosenCity())}
                        onChange={this._onCityTap}/>
                </Paper>
            </div>
            <div style={{width: '100%'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <TextField
                        style={{margin: '0 12px 6px 12px', width: '95%'}}
                        hintText="Улица"
                        floatingLabelText="Улица"
                        ref="street"
                        value={this.state.street}
                        onChange={this._refresh}/>
                </Card>
            </div>
            <div style={{width: '100%'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <TextField
                        style={{margin: '0 12px 6px 12px', width: '95%'}}
                        hintText="Дом"
                        floatingLabelText="Дом"
                        ref="home"
                        value={this.state.home}
                        onChange={this._refresh}/>
                </Card>
            </div>
            <div style={{width: '100%'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <TextField
                        style={{margin: '0 12px 6px 12px', width: '95%'}}
                        hintText="Квартира"
                        floatingLabelText="Квартира"
                        ref="flat"
                        value={this.state.flat}
                        onChange={this._refresh}/>
                </Card>
            </div>
        </div>;
    }
});

export default AddressScreen;