import React from 'react';
import { Card, CardMedia } from 'material-ui';

const MenuItem = React.createClass({
    render() {
        return (
            <Card>
                <CardMedia>
                    <img src={this.props.item.image}/>
                </CardMedia>
                <CardText>
                    {this.props.item.title}
                </CardText>
                <CardText>
                    {this.props.item.description}
                </CardText>
                <CardActions>
                    <FlatButton label={this.props.item.price} />
                </CardActions>
            </Card>
        );
    }
});

export default MenuItem;