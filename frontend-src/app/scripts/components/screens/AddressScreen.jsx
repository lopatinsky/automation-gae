import React from 'react';
import { DropDownMenu, TextField, Paper, Card, FontIcon } from 'material-ui';
import { AddressStore } from '../../stores';
import settings from '../../settings';

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
        return <div style={{padding: '76px 0 0 0'}}>
            <div style={{width: '100%', display: 'table'}}>
                <Paper style={{margin: '0 12px 0 12px', zIndex: '9'}}>
                    <div style={{display: 'table-cell', verticalAlign: 'middle', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '20px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            location_city
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <DropDownMenu
                            style={{zIndex: '10', width: '100%'}}
                            underlineStyle={{display: 'none'}}
                            menuItems={cities}
                            selectedIndex={AddressStore.getCityIndex(AddressStore.getChosenCity())}
                            onChange={this._onCityTap}/>
                    </div>
                </Paper>
            </div>
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '20px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            traffic
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Улица"
                            floatingLabelText="Улица"
                            ref="street"
                            value={this.state.street}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '20px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            domain
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Дом"
                            floatingLabelText="Дом"
                            ref="home"
                            value={this.state.home}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
            <div style={{width: '100%', display: 'table'}}>
                <Card style={{margin: '12px 12px 0 12px'}}>
                    <div style={{display: 'table-cell', padding: '0 9px 0 9px'}}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '20px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            store_mall_directory
                        </FontIcon>
                    </div>
                    <div style={{display: 'table-cell', width: '95%'}}>
                        <TextField
                            style={{width: '100%'}}
                            hintText="Квартира"
                            floatingLabelText="Квартира"
                            ref="flat"
                            value={this.state.flat}
                            onChange={this._refresh}/>
                    </div>
                </Card>
            </div>
        </div>;
    }
});

export default AddressScreen;