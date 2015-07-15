import React from 'react';
import { Input } from 'react-bootstrap';

const InputGroup = React.createClass({
    getInitialState() {
        return {
            showValidation: false,
            valid: true,
            error: null
        };
    },
    render() {
        console.log(this.state);
        return <Input ref='input'
            labelClassName='col-sm-4 col-md-3'
            wrapperClassName={'col-sm-6 col-md-6' + (this.props.label ? '' : 'col-sm-offset-4 col-md-offset-3')}
            hasFeedback
            {...this.props}
            onChange={this._onChange}
            onBlur={this._onBlur}
            bsStyle={this._getBsStyle()}
            help={this.state.error}/>;
    },
    _getBsStyle() {
        if (!this.state.showValidation) {
            return null;
        }
        return this.state.valid ? 'success' : 'error';
    },
    _getHelp() {
        return this.state.showValidation ? this.state.error : '';
    },
    validate(forceEnable=false) {
        if (forceEnable) {
            this.setState({showValidation: true});
        }
        let valid = true, error;
        if (this.props.validators) {
            for (let validator of this.props.validators) {
                let result = validator(this.getValue());
                if (result !== false) {
                    [valid, error] = [false, result];
                    break;
                }
            }
        }
        this.setState({valid, error});
        return valid;
    },
    _onBlur(...args) {
        this.validate(true);
        if (this.props.onBlur) {
            this.props.onBlur.call(this, ...args);
        }
    },
    _onChange(...args) {
        this.validate();
        if (this.props.onChange) {
            this.props.onChange.call(this, ...args);
        }
    },
    getValue() {
        return this.refs.input.getValue();
    }
});

export default InputGroup;
