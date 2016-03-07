import React from 'react';
import { Dialog, FontIcon } from 'material-ui';
import settings from '../../settings';

const SuccessPlaceOrderDialog = React.createClass({
    render() {
        return (
            <Dialog ref="successDialog"
                    bodyStyle={{padding: '12px'}}
                    open={this.props.open}>
                <div style={{display: 'table', width: '100%'}}>
                    <FontIcon style={{display: 'table-cell', verticalAlign: 'middle'}}
                              color={settings.primaryColor}
                              className="material-icons">
                      check_circle
                    </FontIcon>
                    <div style={{display: 'table-cell', paddingLeft: '12px', verticalAlign: 'middle'}}>
                        <b>Заказ успешно размещен!</b>
                    </div>
                </div>
            </Dialog>
        );
    }
});

export default SuccessPlaceOrderDialog;