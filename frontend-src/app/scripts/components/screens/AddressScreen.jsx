import React from 'react';
import DropDownMenu from 'material-ui/lib/drop-down-menu';
import FontIcon from 'material-ui/lib/font-icon';
import MenuItem from 'material-ui/lib/menus/menu-item';
import Paper from 'material-ui/lib/paper';
import TextField from 'material-ui/lib/text-field';
import { AddressStore } from '../../stores';
import { AppActions } from '../../actions';
import settings from '../../settings';

const AddressScreen = React.createClass({
    _onInputChange() {
        this.setState({
            street: this.refs.street.getValue(),
            home: this.refs.home.getValue(),
            flat: this.refs.flat.getValue()
        });
    },

    _onCityTap(e, selectedIndex, city) {
        this.setState({ city });
    },

    saveAddress() {
        AppActions.setAddress({
            city: this.state.city,
            street: this.state.street,
            home: this.state.home,
            flat: this.state.flat
        });
    },

    getInitialState() {
        return {
            city: AddressStore.getChosenCity(),
            street: AddressStore.getStreet(),
            home: AddressStore.getHome(),
            flat: AddressStore.getFlat()
        }
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
                               onChange={this._onInputChange}/>
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
                               onChange={this._onInputChange}/>
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
                               onChange={this._onInputChange}/>
                </div>
            </Paper>
        </div>;
    }
});

export default AddressScreen;