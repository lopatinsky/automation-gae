import React from 'react';
import { List, ListItem, Card, CardMedia, CardText, CardActions, RaisedButton, CardTitle, ListDivider, Icons, IconButton, FontIcon }
    from 'material-ui';
import { MenuItemStore, ModifierStore, OrderStore } from '../../stores';
import { ModifierDialog, SingleModifiersDialog } from '../dialogs';
import { AppActions } from '../../actions';
import Colors from 'material-ui/lib/styles/colors';

const MenuItemScreen = React.createClass({
    _refresh() {
        this.setState({
            item: MenuItemStore.getItem()
        });
    },

    _onModifierTap(modifier) {
        AppActions.setModifier(modifier);
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
                    rightIconButton={<IconButton><Icons.NavigationChevronRight/></IconButton>}
                    primaryText={modifier.chosen_choice.title}
                    onClick={() => this._onModifierTap(modifier)}/>
            );
        });
    },

    _getSingleModifiers() {
        var modifiers = MenuItemStore.getSingleModifiers();
        if (modifiers.length > 0) {
            return <ListItem
                        rightIconButton={<IconButton><Icons.NavigationChevronRight/></IconButton>}
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
        var picCard = <div>
            <CardMedia>
                <img src={item.pic}/>
            </CardMedia>
        </div>;
        var descriptionCard = <div>
            <CardText>{item.description}</CardText>
            <ListDivider/>
        </div>;
        if (item.description == '') {
            descriptionCard = <div/>;
        }
        if (item.pic == null || item.pic == '') {
            picCard = <div/>;
        }
        var grCard = <div/>;
        if (item.weight > 0) {
            grCard = <div>
                <CardText>{item.weight + ' г'}</CardText>
                <ListDivider/>
            </div>;
        }
        if (item.volume > 0) {
            grCard = <div>
                <CardText>{item.volume + ' мл'}</CardText>
                <ListDivider/>
            </div>;
        }
        return (
            <div style={{padding: '76px 0 0 0'}}>
                <Card
                    style={{margin: '0 12px 12px 12px'}}>
                    {picCard}
                    <CardText>{item.title}</CardText>
                    <ListDivider/>
                    {descriptionCard}
                    {grCard}
                    <List style={{paddingTop: '0', paddingBottom: '0'}}>
                        {this._getModifiers()}
                        {this._getSingleModifiers()}
                    </List>
                    <RaisedButton
                        primary={true}
                        style={{margin: '12px', float: 'right'}}
                        label={MenuItemStore.getPrice()}
                        onClick={this._addItem}>
                        <FontIcon style={{verticalAlign: 'middle', fontSize: '18px'}}
                                  color={Colors.white}
                                  className="material-icons">
                            add_shopping_cart
                        </FontIcon>
                    </RaisedButton>
                </Card>
                <ModifierDialog ref="modifierDialog" />
                <SingleModifiersDialog ref="singleModifiersDialog" />
            </div>
        );
    }
});

export default MenuItemScreen;