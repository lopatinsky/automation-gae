import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { AppView, MenuView, MenuItemView, OrderView, VenuesView, HistoryView, AddressView, PromosView, HistoryOrderView, SettingsView, ProfileView }
    from './views';
import injectTapEventPlugin from "react-tap-event-plugin";

injectTapEventPlugin();

const routes = <Route path='/' handler={AppView}>
    <DefaultRoute name='menu' handler={MenuView}/>
    <Route path='/item/:category_id/:item_id/' name='menu_item' handler={MenuItemView}/>
    <Route path='/order' name='order' handler={OrderView}/>
    <Route path='/venues' name='venues' handler={VenuesView}/>
    <Route path='/history' name='history' handler={HistoryView}/>
    <Route path='/address' name='address' handler={AddressView}/>
    <Route path='/profile' name='profile' handler={ProfileView}/>
    <Route path='/promos' name='promos' handler={PromosView}/>
    <Route path='/order/:order_id' name='historyOrder' handler={HistoryOrderView}/>
    <Route path='/settings' name='settings' handler={SettingsView}/>
</Route>;

Router.run(routes, (Handler) => {
    React.render(<Handler/>, document.body);
});
