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
            position: 'fixed',
            left: this.props.horizontal ? 100 : 0,
            right: 0,
            top: this.props.horizontal ? 64 : 164,
            zIndex: 1,
            height: 24,
            background: '#eeeeee',
            textAlign: 'center',
            fontSize: 24,
            lineHeight: '24px',
            paddingTop: 16,
            paddingBottom: 12
        };
        return <div style={style}>
            {this.state.time.format('H:mm:ss')}
            {this.props.children}
        </div>
    }
});
export default Clock;
