import React from 'react';
import { Dialog} from 'material-ui';
import { ModifierStore } from '../../stores';
import ChoicesFragment from './ChoicesFragment';

const ModifierDialog = React.createClass({
    _refresh() {
        this.setState({
            modifier: ModifierStore.getModifier()
        });
    },

    getInitialState: function() {
        return {
            open: false,
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
        this.setState({
            open: true
        });
    },

    dismiss() {
        this.setState({
            open: false
        });
    },

    render() {
        return (
            <Dialog
                autoScrollBodyContent={true}
                ref="modifierDialog"
                open={this.state.open}
                title={this.state.modifier.title}>
                <ChoicesFragment dialog={this}/>
            </Dialog>
        );
    }
});

export default ModifierDialog;