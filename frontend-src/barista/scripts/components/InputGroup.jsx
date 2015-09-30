import React from 'react';
import TextField from 'material-ui/lib/text-field';

const InputGroup = React.createClass({
    getInitialState() {
        return {
            showValidation: false,
            valid: true,
            error: null
        };
    },
    render() {
        return <TextField ref='input'
            {...this.props}
            onChange={this._onChange}
            onBlur={this._onBlur}
            errorText={this._getErrorText()}/>;
    },
    _getErrorText() {
        if (this.props.validators === undefined) {
            return this.props.errorText;
        }
        return this.state.showValidation ? this.state.error : '';
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
