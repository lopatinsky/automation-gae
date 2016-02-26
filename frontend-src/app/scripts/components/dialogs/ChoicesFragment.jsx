import React from 'react';
import { List, ListItem, Divider, FontIcon } from 'material-ui';
import settings from '../../settings';

const ChoicesFragment = React.createClass({
    _onChoiceTap(choice) {
        this.props.onChange(this.props.modifier.modifier_id, choice);
        this.props.requestClose();
    },

    getChoices() {
        if (!this.props.modifier) {
            return null;
        }
        const result = [];
        for (let choice of this.props.modifier.choices) {
            let title = <div style={{display: 'table', width: '100%', tableLayout: 'fixed'}}>
                {choice.price ?
                    <div style={{display: 'table-cell', padding: '0 6px 0 0', width: '30%', verticalAlign: 'middle'}}>
                        <b>{choice.price + 'р.'}</b>
                    </div>
                : null}
                <div style={{display: 'table-cell', verticalAlign: 'middle'}}>
                    {choice.title}
                </div>
                <div style={{display: 'table-cell', textAlign: 'right'}}>
                    {choice == this.props.chosen ?
                        <FontIcon style={{verticalAlign: 'middle'}}
                                  color={settings.primaryColor}
                                  className="material-icons">
                            done
                        </FontIcon>
                    : null}
                </div>
            </div>;
            result.push(<ListItem key={choice.id}
                                  primaryText={title}
                                  onClick={() => this._onChoiceTap(choice)}/>);
            result.push(<Divider key={`divider_${choice.id}`}/>);
        }
        result.pop();
        return result;
    },

    render() {
        return (
            <List>{this.getChoices()}</List>
        );
    }
});

export default ChoicesFragment;
