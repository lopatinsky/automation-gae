import React from 'react';
import { Dialog, TextField, FlatButton } from 'material-ui';
import { OrderStore } from '../../stores';

const CommentDialog = React.createClass({
    _refresh() {
        this.setState({
            comment: this.refs.comment.getValue()
        });
    },

    _submit() {
        OrderStore.setComment(this.refs.comment.getValue());
        this.dismiss();
    },

    show() {
        this.setState({
            open: true,
            comment: OrderStore.getComment()
        });
    },

    dismiss() {
        this.setState({
            open: false
        })
    },

    getInitialState() {
        return {
            open: false,
            comment: OrderStore.getComment()
        }
    },

    render() {
        const actions = [
            <FlatButton label="OK" key="ok" secondary={true} onTouchTap={this._submit}/>,
            <FlatButton label="Отмена" key="cancel" onTouchTap={this.dismiss}/>
        ];
        return (
            <Dialog
                bodyStyle={{padding: '12px 24px'}}
                actions={actions}
                open={this.state.open}
                ref="commentDialog">
                <TextField
                    style={{width: '100%'}}
                    hintText="Комментарий"
                    ref="comment"
                    value={this.state.comment}
                    onChange={this._refresh} />
            </Dialog>
        );
    }
});

export default CommentDialog;