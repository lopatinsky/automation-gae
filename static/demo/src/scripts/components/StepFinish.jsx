import React from 'react';
import { Button } from 'react-bootstrap';
import Actions from '../Actions.js';
import InfoStore from '../stores/InfoStore';

const StepFinish = React.createClass({
    getInitialState() {
        return InfoStore.getLoginPassword();
    },
    render() {
        return <div className="card-container">
            <h4 style={{textAlign: 'center'}}>Готово!</h4>
            <p className="lead" style={{textAlign: 'center'}}>
                Вы можете загрузить демо-приложение и делать с ним все, что угодно :)
            </p>
            <p style={{textAlign: 'center'}}>
                Данные для входа в приложение:<br/>
                логин: <b>{this.state.login}</b><br/>
                пароль: <b>{this.state.password}</b>
            </p>
            <div style={{textAlign: 'center'}}>
                <Button onClick={Actions.restart}>Вернуться в начало</Button>
            </div>
        </div>;
    }
});
export default StepFinish;
