import React from 'react';
import { ButtonLink } from 'react-router-bootstrap';

const InitState = React.createClass({
    render() {
        return <div>
            <h4>Hello</h4>
            <ButtonLink bsStyle="primary" to="step1">Start</ButtonLink>
        </div>;
    }
});
export default InitState;
