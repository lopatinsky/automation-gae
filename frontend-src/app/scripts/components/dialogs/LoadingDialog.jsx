import React from 'react';
import { Dialog, CircularProgress } from 'material-ui';

const LoadingDialog = React.createClass({
    getInitialState() {
        return { open: false };
    },

    show() {
        this.setState({ open: true });
    },

    dismiss() {
        this.setState({ open: false });
    },

    render() {
        return (
            <Dialog open={this.state.open}
                    bodyStyle={{padding: '12px'}}>
                <div style={{display: 'table', width: '100%'}}>
                    <div style={{display: 'table-cell', width: 1, verticalAlign: 'middle'}}>
                        <CircularProgress/>
                    </div>
                    <div style={{display: 'table-cell', paddingLeft: '12px', verticalAlign: 'middle'}}>
                        {this.props.title}
                    </div>
                </div>
            </Dialog>
        );
    }
});

export default LoadingDialog;