import _ from './inject';
import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { RootView, LoginView, MainView, CurrentView, DeliveryView, ReturnsView, HistoryView, StopListView }
    from './views';

const routes = <Route path='/' handler={RootView}>
    <Route name='login' path='login' handler={LoginView}/>
    <Route handler={MainView}>
        <DefaultRoute name='current' handler={CurrentView}/>
        <Route name='delivery' path='delivery' handler={DeliveryView}/>
        <Route name='returns' path='returns' handler={ReturnsView}/>
        <Route name='history' path='history' handler={HistoryView}/>
        <Route name='stoplist' path='stoplist' handler={StopListView}/>
    </Route>
</Route>;

Router.run(routes, (Handler) => {
    React.render(<Handler/>, document.body);
});
