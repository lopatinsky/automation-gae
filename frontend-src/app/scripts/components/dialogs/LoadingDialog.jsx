import React from 'react';
import { Dialog, RefreshIndicator } from 'material-ui';

const LoadingDialog = React.createClass({

    show() {
        this.refs.processingDialog.show();
    },

    dismiss() {
        this.refs.processingDialog.dismiss();
    },

    render() {
        return (
            <Dialog ref="processingDialog"
                    bodyStyle={{padding: '12px'}}>
                <div style={{display: 'table', width: '100%'}}>
                    <div style={{display: 'table-cell', height: '40', width: '40', verticalAlign: 'middle'}}>
                        <RefreshIndicator left={12} top={12} size={40} status="loading" />
                    </div>
                    <div style={{display: 'table-cell', paddingLeft: '12px', verticalAlign: 'middle'}}>
                        <b>{this.props.title}</b>
                    </div>
                </div>
            </Dialog>
        );
    }
});

export default LoadingDialog;