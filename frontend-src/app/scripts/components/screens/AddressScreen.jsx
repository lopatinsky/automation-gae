import React from 'react';
import { DropDownMenu, TextField, Paper, Card, FontIcon, MenuItem } from 'material-ui';
import { AddressStore } from '../../stores';
import settings from '../../settings';

const AddressScreen = React.createClass({
     _onAddressStoreChange() {
        this.setState({
            street: this.refs.street.getValue(),
            home: this.refs.home.getValue(),
            flat: this.refs.flat.getValue()
        });
    },

    _onCityTap(e, selectedIndex, city) {
        AddressStore.setChosenCity(city);
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
        AddressStore.addChangeListener(this._onAddressStoreChange);
    },

    componentWillUnmount() {
        AddressStore.removeChangeListener(this._onAddressStoreChange);
    },

    render() {
        var cities = AddressStore.getCities().map((city, i) => {
            return <MenuItem key={city} value={city} primaryText={city}/>
        });
        return <div style={{paddingTop: 76}}>
            <Paper style={{margin: '0 12px 0 12px', padding: '0 9px 0 9px'}}>
                <div style={{display: 'flex', alignItems: 'center'}}>
                    <FontIcon style={{flexBasis: 36, flexShrink: 0}}
                              color={settings.primaryColor}
                              className="material-icons">
                        location_city
                    </FontIcon>
                    <DropDownMenu style={{flexGrow: 1, flexShrink: 0, margin: '0 -24px'}}
                                  value={AddressStore.getChosenCity()}
                                  onChange={this._onCityTap}>
                        {cities}
                    </DropDownMenu>
                </div>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        traffic
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               floatingLabelText="Улица"
                               ref="street"
                               value={this.state.street}
                               onChange={this._refresh}/>
                </div>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        domain
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               floatingLabelText="Дом"
                               ref="home"
                               value={this.state.home}
                               onChange={this._refresh}/>
                </div>
                <div style={{display: 'flex', alignItems: 'baseline'}}>
                    <FontIcon style={{flexBasis: 36}}
                              color={settings.primaryColor}
                              className="material-icons">
                        store_mall_directory
                    </FontIcon>
                    <TextField style={{flexGrow: 1}}
                               floatingLabelText="Квартира"
                               ref="flat"
                               value={this.state.flat}
                               onChange={this._refresh}/>
                </div>
            </Paper>
        </div>;
    }
});

export default AddressScreen;