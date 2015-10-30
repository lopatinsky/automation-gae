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
        this.setState({
            comment: OrderStore.getComment()
        });
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
            <Dialog
                bodyStyle={{padding: '12px 24px'}}
                actions={[{text: 'Ок', onTouchTap: this._submit}, {text: 'Отмена', onTouchTap: this.dismiss}]}
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