import React from 'react';
import { List, ListItem, Card, CardMedia, CardText, CardActions, FlatButton, CardTitle } from 'material-ui';
import { MenuItemStore, ModifierStore } from '../stores';
import { ModifierDialog } from '../components';
import Actions from '../Actions';

const MenuItemScreen = React.createClass({

    _refresh() {
        this.setState({
            item: MenuItemStore.getItem()
        });
    },

    _onModifierTap(modifier) {
        Actions.setModifier(modifier);
        this.refs.modifierDialog.show();
    },

    _getModifiers() {
        var modifiers = MenuItemStore.getModifiers();
        return modifiers.map(modifier => {
            return (
                <ListItem
                    primaryText={modifier.chosen_choice.title}
                    onClick={() => this._onModifierTap(modifier)}/>
            );
        });
    },

    getInitialState: function() {
        return {
            item: MenuItemStore.getItem()
        }
    },

    componentDidMount() {
        MenuItemStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        MenuItemStore.removeChangeListener(this._refresh);
    },

    render() {
        var item = this.state.item;
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