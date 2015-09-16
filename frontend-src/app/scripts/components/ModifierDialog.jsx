import React from 'react';
import { Dialog} from 'material-ui';
import { ModifierStore } from '../stores';
import { ChoicesFragment } from '../components';

const ModifierDialog = React.createClass({
    _refresh() {
        this.setState({
            modifier: ModifierStore.getModifier()
        });
    },

    getInitialState: function() {
        return {
            modifier: {
                title: 'Не загружено'
            }
        }
    },

    componentDidMount() {
        ModifierStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        ModifierStore.removeChangeListener(this._refresh);
    },

    show() {
        this.refs.modifierDialog.show();
    },

    dismiss() {
         this.refs.modifierDialog.dismiss();
    },

    render() {
        return (
            <Dialog ref="modifierDialog" title={this.state.modifier.title}>
                <ChoicesFragment dialog={this}/>
            </Dialog>
        );
    }
});

export default ModifierDialog;