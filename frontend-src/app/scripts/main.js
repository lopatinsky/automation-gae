import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { AppView, MenuView } from './views';
import injectTapEventPlugin from "react-tap-event-plugin";

injectTapEventPlugin();

const routes = <Route path='/' handler={AppView}>
    <DefaultRoute handler={MenuView}/>
</Route>;

Router.run(routes, (Handler) => {
    React.render(<Handler/>, document.body);
});
