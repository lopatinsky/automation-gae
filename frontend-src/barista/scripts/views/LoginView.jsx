import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardTitle from 'material-ui/lib/card/card-title';
import CardText from 'material-ui/lib/card/card-text';
import CardActions from 'material-ui/lib/card/card-actions';
import FlatButton from 'material-ui/lib/flat-button';
import Snackbar from 'material-ui/lib/snackbar';
import { InputGroup, SpinnerWrap } from '../components';
import { required } from '../validators';
import Actions from '../Actions';
import { AuthStore, AjaxStore } from '../stores';

const LoginView = React.createClass({
    statics: {
        onEnter(nextState, replace) {
            if (AuthStore.token) {
                replace('/current');
            }
        }
    },

    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

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
            }
        };
    },
    getInitialState() {
        return {
            loggingIn: AuthStore.loggingIn,
            errorShow: false,
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
            setImmediate(() => {
                this.context.router.push("/current");
            });
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
            this.setState({
                errorShow: true,
                errorMessage
            });
        }
    },
    render() {
        let styles = this._getStyles();
        return <div style={styles.outer}>
            <div style={styles.inner}>
                <div style={styles.card}>
                    <Card>
                        <CardTitle title='Вход'/>
                        <SpinnerWrap show={this.state.loggingIn}>
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
                        </SpinnerWrap>
                    </Card>
                    <Snackbar ref='error'
                              message={this.state.errorMessage}
                              autoHideDuration={5000}
                              open={this.state.errorShow}
                              onRequestClose={() => { this.setState({ errorShow: false }); }}/>
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
