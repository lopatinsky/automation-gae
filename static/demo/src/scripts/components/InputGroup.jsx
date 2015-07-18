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
        return <Input ref='input'
            hasFeedback
            {...this.props}
            onChange={this._onChange}
            onBlur={this._onBlur}
            bsStyle={this._getBsStyle()}
            help={this._getHelp()}/>;
    },
    _getHelp() {
        if (this.props.noValidation) {
            return this.props.help;
        }
        return this.state.showValidation ? this.state.error : '';
    },
    _getBsStyle() {
        if (this.props.noValidation) {
            return this.props.bsStyle;
        }
        if (!this.state.showValidation) {
            return null;
        }
        return this.state.valid ? 'success' : 'error';
    },
    componentWillReceiveProps() {
        this.validate();
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
