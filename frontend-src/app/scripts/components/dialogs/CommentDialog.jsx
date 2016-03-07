import React from 'react';
import Dialog from 'material-ui/lib/dialog';
import FlatButton from 'material-ui/lib/flat-button';
import TextField from 'material-ui/lib/text-field';
import { OrderStore } from '../../stores';
import { AppActions } from '../../actions';

const CommentDialog = React.createClass({
    _submit() {
        AppActions.setComment(this.state.comment);
        this.dismiss();
    },

    show() {
        this.setState({
            open: true
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
            comment: OrderStore.comment
        }
    },

    _onOrderStoreChanged() {
        this.setState({
            comment: OrderStore.comment
        });
    },

    _onChange() {
        this.setState({
            comment: this.refs.comment.getValue()
        });
    },

    componentDidMount() {
        OrderStore.addChangeListener(this._onOrderStoreChanged);
    },

    componentWillUnmount() {
        OrderStore.removeChangeListener(this._onOrderStoreChanged);
    },

    render() {
        const actions = [
            <FlatButton label="Отмена" key="cancel" onTouchTap={this.dismiss}/>,
            <FlatButton label="OK" key="ok" secondary={true} onTouchTap={this._submit}/>
        ];
        return (
            <Dialog
                bodyStyle={{padding: '12px 24px'}}
                actions={actions}
                open={this.state.open}
                ref="commentDialog">
                <TextField style={{width: '100%'}}
                           hintText="Комментарий"
                           ref="comment"
                           onRequestClose={this.dismiss}
                           value={this.state.comment}
                           onChange={this._onChange}/>
            </Dialog>
        );
    }
});

export default CommentDialog;