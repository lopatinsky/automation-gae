import React from 'react';
import { Button } from 'react-bootstrap';
import Actions from '../Actions.js';

const StepFinish = React.createClass({
    render() {
        return <div>
            <h3>Finished!</h3>
            <Button onClick={Actions.restart}>Start over</Button>
        </div>;
    }
});
export default StepFinish;
