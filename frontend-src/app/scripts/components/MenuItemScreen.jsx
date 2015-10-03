import React from 'react';
import { List, ListItem, Card, CardMedia, CardText, CardActions, FlatButton, CardTitle } from 'material-ui';
import { MenuItemStore, ModifierStore, OrderStore } from '../stores';
import { ModifierDialog, SingleModifiersDialog } from '../components';
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

    _onSingleModifierTap() {
        this.refs.singleModifiersDialog.show();
    },

    _addItem() {
        OrderStore.addItem(MenuItemStore.getItem());
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

    _getSingleModifiers() {
        var modifiers = MenuItemStore.getSingleModifiers();
        if (modifiers.length > 0) {
            return <ListItem
                        primaryText={'Добавки'}
                        onClick={() => this._onSingleModifierTap()}/>;
        }
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
                        <FlatButton label={MenuItemStore.getPrice()} onClick={this._addItem} />
                    </CardActions>
                </Card>
                <List>
                    {this._getModifiers()}
                    {this._getSingleModifiers()}
                </List>
                <ModifierDialog ref="modifierDialog" />
                <SingleModifiersDialog ref="singleModifiersDialog" />
            </div>
        );
    }
});

export default MenuItemScreen;