import React from 'react';
import { Route, DefaultRoute } from 'react-router';
import App from './App';
import Step1 from './Step1';
import Step2 from './Step2';
import Step3 from './Step3';
import StepFinish from './StepFinish';

const routes = (
    <Route handler={App} path="/">
        <Route name="step1" path="step1" handler={Step1} />
        <Route name="step2" path="step2" handler={Step2} />
        <Route name="step3" path="step3" handler={Step3} />
        <Route name="finish" path="finish" handler={StepFinish} />
        <DefaultRoute handler={Step1} />
    </Route>
);
export default routes;
