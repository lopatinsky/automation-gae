import React from 'react';
import moment from 'moment';

const Clock = React.createClass({
    _updateInterval: null,
    getInitialState() {
        return { time: moment() };
    },
    componentDidMount() {
        this._updateInterval = setInterval(() => this.setState({ time: moment()}), 1000);
    },
    componentWillUnmount() {
        clearInterval(this._updateInterval);
    },
    render() {
        const style = {
            textAlign: 'center',
            fontSize: 24,
            paddingBottom: 12
        };
        return <div style={style}>{this.state.time.format('H:mm:ss')}</div>
    }
});
export default Clock;
