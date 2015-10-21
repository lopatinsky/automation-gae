import React from 'react';

const HistoryOrderItem = React.createClass({

    render() {
        var item = this.props.item;
        return (
            <div style={{padding: '12px'}}>
                <b>{item.title}</b>
            </div>
        );
    }
});

export default HistoryOrderItem;