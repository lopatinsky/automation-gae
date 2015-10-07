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
                height: 48,
                background: '#eeeeee',
                textAlign: 'center',
                fontSize: 24,
                paddingTop: 4
            },
            contentStyle = {
                lineHeight: '48px'
            };
        let content = <span style={contentStyle}>{this.state.time.format('H:mm:ss')}</span>
        if (this.props.lastUpdate) {
            const seconds = this.state.time.diff(this.props.lastUpdate, 'seconds');
            if (seconds > 30) {
                content = <span style={{color: 'red', ...contentStyle}}>Проверьте интернет!</span>
            }
        }
        return <div style={style}>
            {content} {this.props.children}
        </div>;
    }
});
export default Clock;
