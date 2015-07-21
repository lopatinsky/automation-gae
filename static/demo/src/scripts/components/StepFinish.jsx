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
                <a href="http://rbcn.mobi/get/dem?m=finish" target="_blank">Скачайте демо-приложение</a> или
                отсканируйте QR-код ниже:
            </p>
            <div style={{textAlign: 'center'}}>
                <img src="http://chart.apis.google.com/chart?cht=qr&chs=540x540&chl=http%3A//rbcn.mobi/get/dem%3Fm%3Dqr&chld=L|0" alt="QR" width={270}/>
            </div>
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
