import React from 'react';
import { List, ListItem, Card, CardMedia, CardText, CardActions, RaisedButton, CardTitle, Divider, Icons, IconButton, FontIcon }
    from 'material-ui';
import { MenuStore } from '../../stores';
import { ModifierDialog, SingleModifiersDialog } from '../dialogs';
import { AppActions } from '../../actions';
import Colors from 'material-ui/lib/styles/colors';

const MenuItemScreen = React.createClass({
    getInitialState() {
        const groupModifiers = {},
            singleModifiers = {};
        for (let mod of this.props.item.group_modifiers) {
            groupModifiers[mod.modifier_id] = MenuStore.getDefaultModifierChoice(mod);
        }
        for (let mod of this.props.item.single_modifiers) {
            singleModifiers[mod.modifier_id] = 0;
        }
        return {
            groupModifiers,
            singleModifiers,
            openSingleModifiers: false,
            openedGroupModifier: null
        };
    },

    _onModifierTap(modifier) {
        this.setState({openedGroupModifier: modifier});
    },

    _onSingleModifierTap() {
        this.setState({openSingleModifiers: true});
    },

    _addItem() {
        AppActions.addItem(this.props.item.id, this.state.groupModifiers, this.state.singleModifiers);
    },

    _getModifiersTitles() {
        var modifiers = this.props.item.group_modifiers;
        var sModifiers = this.props.item.single_modifiers;
        var count = 0;
        var result = <div>
            <CardText>
                {modifiers.map(modifier => {
                    count += 1;
                    let chosenChoice = this.state.groupModifiers[modifier.modifier_id];
                    return <div key={modifier.modifier_id} style={{lineHeight: '120%'}}>
                        {chosenChoice ? chosenChoice.title : 'Не выбрано'}
                        {chosenChoice && chosenChoice.price > 0 ?
                            <div style={{float: 'right'}}>
                                {'+ ' + chosenChoice.price + ' р.'}
                            </div>
                        : null}
                    </div>;
                })}
                {sModifiers.map(modifier => {
                    const quantity = this.state.singleModifiers[modifier.modifier_id];
                    if (!quantity) {
                        return null;
                    }
                    count += 1;
                    return <div key={modifier.modifier_id} style={{lineHeight: '120%'}}>
                        {modifier.title + ' x' + quantity}
                        <div style={{float: 'right'}}>
                            {'+ ' + (modifier.price * quantity) + ' р.'}
                        </div>
                    </div>;
                })}
            </CardText>
            <Divider/>
        </div>;
        if (count > 0) {
            return result;
        } else {
            return null;
        }
    },

    _getModifiers() {
        var modifiers = this.props.item.group_modifiers;
        return modifiers.map(modifier => {
            let chosenChoice = this.state.groupModifiers[modifier.modifier_id];
            return (
                <ListItem key={modifier.modifier_id}
                    rightIconButton={<IconButton><Icons.NavigationChevronRight/></IconButton>}
                    primaryText={chosenChoice ? chosenChoice.title : 'Не выбрано'}
                    onTouchTap={() => this._onModifierTap(modifier)}/>
            );
        });
    },

    _getSingleModifiers() {
        var modifiers = this.props.item.single_modifiers;
        if (modifiers.length > 0) {
            return <ListItem
                        rightIconButton={<IconButton><Icons.NavigationChevronRight/></IconButton>}
                        primaryText={'Добавки'}
                        onTouchTap={() => this._onSingleModifierTap()}/>;
        }
    },

    _onSingleModifierChange(id, newQuantity) {
        this.setState({
            singleModifiers: {
                ...this.state.singleModifiers,
                [id]: newQuantity
            }
        });
    },

    _onGroupModifierChange(id, newChoice) {
        this.setState({
            groupModifiers: {
                ...this.state.groupModifiers,
                [id]: newChoice
            }
        });
    },

    _onModifierClose() {
        this.setState({
            openSingleModifiers: false,
            openedGroupModifier: null
        });
    },

    render() {
        var item = this.props.item;
        var nameAndPic = item.pic ? <CardMedia overlay={<CardTitle title={item.title}/>}>
            <img src={item.pic}/>
        </CardMedia> : <CardTitle title={item.title}/>;
        var descriptionCard = item.description ? <CardText>{item.description}</CardText> : null;
        var grCard = null;
        if (item.weight > 0) {
            grCard = <CardText>{item.weight + ' г'}</CardText>;
        } else if (item.volume > 0) {
            grCard = <CardText>{item.volume + ' мл'}</CardText>;
        }
        const btnIcon = <FontIcon className="material-icons">
            add_shopping_cart
        </FontIcon>;
        return (
            <div style={{padding: '76px 0 0 0'}}>
                <Card
                    style={{margin: '0 12px 12px 12px'}}>
                    {nameAndPic}
                    {descriptionCard}
                    {descriptionCard && <Divider/>}
                    {grCard}
                    {grCard && <Divider/>}
                    {this._getModifiersTitles()}
                    <List style={{paddingTop: '0', paddingBottom: '0'}}>
                        {this._getModifiers()}
                        {this._getSingleModifiers()}
                    </List>
                    <RaisedButton
                        primary={true}
                        style={{margin: '12px', float: 'right'}}
                        label={MenuStore.getItemPrice(this.props.item, this.state.groupModifiers, this.state.singleModifiers)}
                        icon={btnIcon}
                        onTouchTap={this._addItem}/>
                </Card>
                <ModifierDialog ref="modifierDialog"
                                modifier={this.state.openedGroupModifier}
                                chosenChoices={this.state.groupModifiers}
                                onChange={this._onGroupModifierChange}
                                open={!!this.state.openedGroupModifier}
                                requestClose={this._onModifierClose}/>
                <SingleModifiersDialog ref="singleModifiersDialog"
                                       modifiers={item.single_modifiers}
                                       quantities={this.state.singleModifiers}
                                       onChange={this._onSingleModifierChange}
                                       open={this.state.openSingleModifiers}
                                       requestClose={this._onModifierClose}/>
            </div>
        );
    }
});

export default MenuItemScreen;