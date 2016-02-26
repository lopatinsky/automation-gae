import _ from './inject';
import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, Redirect, hashHistory } from 'react-router';
import { AppView, MenuView, MenuItemView, OrderView, VenuesView, HistoryView, AddressView, PromosView, HistoryOrderView, SettingsView, ProfileView }
    from './views';

const routes = <Route path='/' component={AppView}>
    <Route path='/menu' component={MenuView}/>
    <Route path='/menu/:category_id' component={MenuView}/>
    <Route path='/item/:category_id/:item_id' component={MenuItemView}/>
    <Route path='/order' component={OrderView}/>
    <Route path='/venues' component={VenuesView}/>
    <Route path='/history' component={HistoryView}/>
    <Route path='/address' component={AddressView}/>
    <Route path='/profile' component={ProfileView}/>
    <Route path='/promos' component={PromosView}/>
    <Route path='/order/:order_id' component={HistoryOrderView}/>
    <Route path='/settings' component={SettingsView}/>
    <Redirect from='*' to='/menu'/>
</Route>;

ReactDOM.render(<Router routes={routes} history={hashHistory}/>, document.getElementById("app-container"));
