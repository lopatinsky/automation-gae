import React from 'react';
import { Card, CardMedia, CardText, CardActions, FlatButton, CardTitle } from 'material-ui';
import { MenuItemStore } from '../stores';
import Actions from '../Actions';

const MenuItemScreen = React.createClass({
    _onModifierTap(modifier) {
        Actions.setModifier(modifier);
        this.refs.modifierDialog.show();
    },

    _getModifiers() {
        var modifiers = MenuItemStore.getModifiers();
        modifiers.map(modifier => {
            return (
                <ListItem
                    primaryText={modifier.chosen_choice.title}
                    onClick={() => this._onModifierTap(modifier)}/>
            );
        });
    },

    render() {
        var item = MenuItemStore.getItem();
        return (
            <div>
                <Card>
                    <CardMedia overlay={<CardTitle title={item.title}/>}>
                        <img src={item.pic}/>
                    </CardMedia>
                    <CardText>{item.description}</CardText>
                    <CardActions>
                        <FlatButton label={item.price} />
                    </CardActions>
                </Card>
                <List>
                    {this._getModifiers()}
                </List>
                <ModifierDialog ref="modifierDialog" />
            </div>
        );
    }
});

export default MenuItemScreen;