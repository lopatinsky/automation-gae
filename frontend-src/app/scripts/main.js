import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { AppView, MenuView, MenuItemView } from './views';
import injectTapEventPlugin from "react-tap-event-plugin";

injectTapEventPlugin();

const routes = <Route path='/' handler={AppView}>
    <DefaultRoute name='menu' handler={MenuView}/>
    <Route path='/item/:category_id/:item_id/' name='menu_item' handler={MenuItemView}/>
</Route>;

Router.run(routes, (Handler) => {
    React.render(<Handler/>, document.body);
});
