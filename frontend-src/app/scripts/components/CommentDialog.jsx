import React from 'react';
import { Dialog, TextField, FlatButton } from 'material-ui';
import { OrderStore } from '../stores';
import Actions from '../Actions';

const CommentDialog = React.createClass({
    _refresh() {
        this.setState({});
    },

    _submit() {
        OrderStore.setComment(this.refs.comment);
        this.dismiss();
    },

    show() {
        this.refs.commentDialog.show();
    },

    dismiss() {
         this.refs.commentDialog.dismiss();
    },

    componentDidMount() {
        //ClientStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        //ClientStore.removeChangeListener(this._refresh);
    },

    render() {
        return (
            <Dialog ref="commentDialog">
                <TextField hintText="Комментарий" ref="comment" value={OrderStore.getComment()} onChange={this._setClientInfo}/>
                <FlatButton label="Ок" onClick={this._submit} />
                <FlatButton label="Отмена" onClick={this.dismiss} />
            </Dialog>
        );
    }
});

export default CommentDialog;