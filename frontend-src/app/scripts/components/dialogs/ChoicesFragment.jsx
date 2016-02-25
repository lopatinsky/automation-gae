import React from 'react';
import { List, ListItem, Divider, FontIcon } from 'material-ui';
import { ModifierStore, MenuItemStore } from '../../stores';
import settings from '../../settings';

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
            var title = <div style={{display: 'table', width: '100%', tableLayout: 'fixed'}}>
                {this.state.modifier.with_price ?
                    <div style={{display: 'table-cell', padding: '0 6px 0 0', width: '30%', verticalAlign: 'middle'}}>
                        <b>{choice.price + 'р.'}</b>
                    </div>
                : null}
                <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                    {choice.title}
                </div>
                <div style={{display: 'table-cell', textAlign: 'right'}}>
                    {this.state.modifier.chosen_choice == choice ?
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '32px'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            done
                        </FontIcon>
                    : <div/>}
                </div>
            </div>;
            return <div>
                    <ListItem
                        primaryText={title}
                        onClick={() => this._onChoiceTap(choice)}/>
                    <Divider/>
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