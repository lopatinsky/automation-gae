import React from 'react';
import CircularProgress from 'material-ui/lib/circular-progress';
import Dialog from 'material-ui/lib/dialog';

const LoadingDialog = React.createClass({
    render() {
        return (
            <Dialog open={this.props.open}
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