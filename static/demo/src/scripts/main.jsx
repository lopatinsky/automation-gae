import React from 'react';
import Router, { RouteHandler, DefaultRoute, Route } from 'react-router';
import routes from './components/routes';

Router.run(routes, Handler => {
    React.render(<Handler/>, document.body);
});
