import React from 'react';
import { Input as RBInput } from 'react-bootstrap';

const Input = React.createClass({
    render() {
        return <RBInput ref='input'
            labelClassName='col-sm-4 col-md-3'
            wrapperClassName={'col-sm-6 col-md-6' + (this.props.label ? '' : 'col-sm-offset-4 col-md-offset-3')}
            hasFeedback
            {...this.props}/>;
    },
    getValue() {
        return this.refs.input.getValue();
    }
});

export default Input;
