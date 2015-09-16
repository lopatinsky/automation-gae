import React from 'react';
import { List, ListItem } from 'material-ui';
import { ModifierStore, MenuItemStore } from '../stores';

const ChoicesFragment = React.createClass({
    _refresh() {
        this.setState({
            modifier: ModifierStore.getModifier()
        });
    },

    _onChoiceTap(choice) {
        MenuItemStore.setChoice(ModifierStore.getModifier(), choice);
        this.props.dialog.dismiss();
    },

    getInitialState: function() {
        return {
            modifier: ModifierStore.getModifier()
        }
    },

    componentDidMount() {
        ModifierStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        ModifierStore.removeChangeListener(this._refresh);
    },

    getChoices() {
        var choices = this.state.modifier.choices;
        return choices.map(choice => {
            return (
                <ListItem
                    primaryText={choice.title}
                    onClick={() => this._onChoiceTap(choice)}/>
            );
        });
    },

    render() {
        return (
            <List>{this.getChoices()}</List>
        );
    }
});

export default ChoicesFragment;