import React from 'react';
import { Card, CardText, FlatButton } from 'material-ui';
import { MenuItemStore } from '../stores';

const SingleModifier = React.createClass({
    _refresh() {
        this.setState({});
    },

    _add(modifier) {
        MenuItemStore.addSingleModifier(modifier.modifier_id);
    },

    _deduct(modifier) {
        MenuItemStore.deductSingleModifier(modifier.modifier_id);
    },

    componentDidMount() {
        MenuItemStore.addChangeListener(this._refresh);
    },

    componentWillUnmount() {
        MenuItemStore.removeChangeListener(this._refresh);
    },

    render() {
        var modifier = this.props.modifier;
        return (
            <Card>
                <FlatButton label="-" onClick={() => this._deduct(modifier)} />
                <CardText>
                    {modifier.title}:: {modifier.quantity}
                </CardText>
                <FlatButton label="+" onClick={() => this._add(modifier)} />
            </Card>
        );
    }
});

export default SingleModifier;