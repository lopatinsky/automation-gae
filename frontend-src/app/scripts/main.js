import _ from './inject';
import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';
import { AppView, MenuView, MenuItemView, OrderView, VenuesView, HistoryView, AddressView, PromosView, HistoryOrderView, SettingsView, ProfileView }
    from './views';

const routes = <Route path='/' component={AppView}>
    <IndexRoute name='menu' component={MenuView}/>
    <Route path='/item/:category_id/:item_id/' name='menu_item' component={MenuItemView}/>
    <Route path='/order' name='order' component={OrderView}/>
    <Route path='/venues' name='venues' component={VenuesView}/>
    <Route path='/history' name='history' component={HistoryView}/>
    <Route path='/address' name='address' component={AddressView}/>
    <Route path='/profile/:settings?' name='profile' component={ProfileView}/>
    <Route path='/promos' name='promos' component={PromosView}/>
    <Route path='/order/:order_id' name='historyOrder' component={HistoryOrderView}/>
    <Route path='/settings' name='settings' component={SettingsView}/>
</Route>;

ReactDOM.render(<Router routes={routes} history={hashHistory}/>, document.getElementById("app-container"));
