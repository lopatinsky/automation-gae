import React from 'react';
import { Navigation } from 'react-router';
import { Card, CardTitle, CardText, CardActions, FlatButton, CircularProgress, Snackbar } from 'material-ui';
import { InputGroup } from '../components';
import { required } from '../validators';
import Actions from '../Actions';
import { AuthStore, AjaxStore } from '../stores';

const LoginView = React.createClass({
    statics: {
        willTransitionTo(transition) {
            if (AuthStore.token) {
                transition.redirect('current');
            }
        }
    },

    mixins: [Navigation],

    loginValidators: [required('Введите логин')],
    passwordValidators: [required('Введите пароль')],
    _getStyles() {
        return {
            outer: {
                height: '100%',
                width: '100%',
                display: 'table'
            }, inner: {
                display: 'table-cell',
                textAlign: 'center',
                verticalAlign: 'middle'
            }, card: {
                display: 'inline-block',
                textAlign: 'left',
                margin: '0 auto',
                position: 'relative'
            }, progress: {
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginLeft: -25,
                marginTop: -25
            }
        }
    },
    getInitialState() {
        return {
            loggingIn: AuthStore.loggingIn,
            errorMessage: ''
        };
    },
    componentDidMount() {
        AuthStore.addChangeListener(this._onAuthStoreUpdate);
        AjaxStore.addChangeListener(this._onAjaxStoreUpdate);
    },
    componentWillUnmount() {
        AuthStore.removeChangeListener(this._onAuthStoreUpdate);
        AjaxStore.removeChangeListener(this._onAjaxStoreUpdate);
    },
    _onAuthStoreUpdate() {
        if (AuthStore.token) {
            this.transitionTo('current');
        }
    },
    _onAjaxStoreUpdate(data) {
        this.setState({ loggingIn: AjaxStore.sending.login });
        if (data && data.status) {
            let errorMessage;
            if (data.status == 401) {
                errorMessage = 'Неверный логин или пароль, попробуйте еще раз';
            } else {
                errorMessage = 'Неизвестная ошибка, попробуйте еще раз';
            }
            this.setState({ errorMessage });
            this.refs.error.show();
        }
    },
    render() {
        let styles = this._getStyles();
        return <div style={styles.outer}>
            <div style={styles.inner}>
                <div style={styles.card}>
                    <Card>
                        <CardTitle title='Вход'/>
                        <div style={{opacity: this.state.loggingIn ? 0 : 1}}>
                            <CardText style={{paddingTop:0, paddingBottom:0}}>
                                <InputGroup ref='login'
                                            floatingLabelText='Логин'
                                            fullWidth={true}
                                            onEnterKeyDown={this.submit}
                                            disabled={this.state.loggingIn}
                                            validators={this.loginValidators}/>
                                <InputGroup ref='password'
                                            type='password'
                                            floatingLabelText='Пароль'
                                            fullWidth={true}
                                            onEnterKeyDown={this.submit}
                                            disabled={this.state.loggingIn}
                                            validators={this.passwordValidators}/>
                            </CardText>
                            <CardActions style={{textAlign:'right'}}>
                                <FlatButton label='Войти' secondary={true} onTouchTap={this.submit} disabled={this.state.loggingIn}/>
                            </CardActions>
                        </div>
                        {this.state.loggingIn && <CircularProgress style={styles.progress}/>}
                    </Card>
                    <Snackbar ref='error' message={this.state.errorMessage} autoHideDuration={5000}/>
                </div>
            </div>
        </div>;
    },
    submit() {
        // need to validate both, so intentionally not using ||
        //noinspection JSBitwiseOperatorUsage
        if (!this.refs.login.validate(true) | !this.refs.password.validate(true)) {
            return;
        }
        Actions.login(this.refs.login.getValue(), this.refs.password.getValue());
    }
});
export default LoginView;
