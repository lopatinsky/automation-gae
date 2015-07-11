import React from 'react';
import { ButtonLink } from 'react-router-bootstrap';

const Step2 = React.createClass({
    render() {
        return <div>
            <h4>This is step 2</h4>
            <ButtonLink bsStyle="primary" to="step3">Next</ButtonLink>
        </div>;
    }
});
export default Step2;
