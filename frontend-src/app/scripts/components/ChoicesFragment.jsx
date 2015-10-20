import React from 'react';
import { List, ListItem, ListDivider } from 'material-ui';
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
            var title = choice.title;
            if (choice.price > 0) {
                title = <div style={{display: 'table'}}>
                    <div style={{display: 'table-cell', padding: '0 6px 0 0'}}>
                        <b>{choice.price + 'р.'}</b>
                    </div>
                    <div style={{display: 'table-cell'}}>
                        {choice.title}
                    </div>
                </div>;
            }
            return <div>
                    <ListItem
                        primaryText={title}
                        onClick={() => this._onChoiceTap(choice)}/>
                    <ListDivider/>
                </div>;
        });
    },

    render() {
        return (
            <List>{this.getChoices()}</List>
        );
    }
});

export default ChoicesFragment;