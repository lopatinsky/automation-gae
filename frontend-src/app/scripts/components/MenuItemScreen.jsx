import React from 'react';
import { Card, CardMedia, CardText, CardActions, FlatButton, CardTitle } from 'material-ui';

const MenuItemScreen = React.createClass({
    render() {
        var item = this.props.item;
        return (
            <Card>
                <CardMedia overlay={<CardTitle title={item.title}/>}>
                    <img src={item.pic}/>
                </CardMedia>
                <CardText>{item.description}</CardText>
                <CardActions>
                    <FlatButton label={item.price}/>
                </CardActions>
            </Card>
        );
    }
});

export default MenuItemScreen;