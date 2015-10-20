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
        this.refs.commentDialog.show();
    },

    dismiss() {
        this.refs.commentDialog.dismiss();
    },

    getInitialState() {
        return {
            comment: OrderStore.getComment()
        }
    },

    render() {
        return (
            <Dialog ref="commentDialog">
                <TextField
                    style={{width: '100%'}}
                    hintText="Комментарий"
                    ref="comment"
                    value={this.state.comment}
                    onChange={this._refresh} />
                <FlatButton
                    style={{margin: '12px 0 0 0'}}
                    label="Ок"
                    onClick={this._submit} />
                <FlatButton
                    style={{margin: '12px 0 0 12px'}}
                    label="Отмена"
                    onClick={this.dismiss} />
            </Dialog>
        );
    }
});

export default CommentDialog;