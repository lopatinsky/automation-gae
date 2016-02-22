import _ from './inject';
import React from 'react';
import ReactDOM from 'react-dom'
import { Router, Route, IndexRoute, Redirect, hashHistory } from 'react-router';
import { RootView, LoginView, MainView, CurrentView, DeliveryView, ReturnsView, HistoryView, StopListView }
    from './views';

const routes = <Route component={RootView}>
    <Route path='/login' component={LoginView} onEnter={LoginView.onEnter}/>
    <Route component={MainView} onEnter={MainView.onEnter}>
        <Route path='/current' component={CurrentView}/>
        <Route path='/delivery' component={DeliveryView}/>
        <Route path='/returns' component={ReturnsView}/>
        <Route path='/history' component={HistoryView}/>
        <Route path='/stoplist' component={StopListView}/>
    </Route>
    <Redirect from='*' to='/current' />
</Route>;

ReactDOM.render(<Router routes={routes} history={hashHistory}/>, document.getElementById("app-container"));
