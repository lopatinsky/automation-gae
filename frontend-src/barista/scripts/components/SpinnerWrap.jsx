import React from 'react';
import { CircularProgress, Styles } from 'material-ui';
const AutoPrefix = Styles.AutoPrefix;

const SpinnerWrap = React.createClass({
    getDefaultProps() {
        return {
            show: false
        };
    },
    render() {
        const progressStyles = AutoPrefix.all({
                transition: 'opacity 0.2s linear',
                visibility: this.props.show ? 'visible' : 'hidden',
                opacity: this.props.show ? 1 : 0,
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginLeft: -25,
                marginTop: -25
            }),
            contentStyles = AutoPrefix.all({
                transition: 'opacity 0.2s linear',
                opacity: this.props.show ? 0 : 1
            });
        return <div style={{position: 'relative'}}>
            <CircularProgress style={progressStyles}/>
            <div style={contentStyles}>
                {this.props.children}
            </div>
        </div>;
    }
});
export default SpinnerWrap;
