import _ from './inject';
import React from 'react';
import Router, { Route, DefaultRoute } from 'react-router';
import { soundManager } from 'soundmanager2';
import { RootView, LoginView, MainView, CurrentView, DeliveryView, ReturnsView, HistoryView, StopListView }
    from './views';

soundManager.setup({
    url: '/static/barista/swf',
    debugMode: false,
    onready() {
        soundManager.createSound({
            id: 'new_orders',
            url: '/static/barista/sounds/ship_horn.mp3',
            autoLoad: true
        });
    }
});

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
