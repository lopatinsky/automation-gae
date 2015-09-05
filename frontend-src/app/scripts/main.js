import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { RootView } from './views';
import injectTapEventPlugin from "react-tap-event-plugin";

injectTapEventPlugin();

const routes = <Route path='/' handler={RootView}>
    <Route handler={MainView}></Route>
</Route>;

Router.run(routes, (Handler) => {
    React.render(<Handler/>, document.body);
});
