import React from 'react';
import { State, Link } from 'react-router';
import assign from 'object-assign';

const NavItem = React.createClass({
    mixins: [State],
    _renderLabel() {
        if (this.props.label) {
            const labelStyle = {
                position: 'absolute',
                left: '50%',
                top: '50%',
                width: 28,
                height: 28,
                lineHeight: '28px',
                marginLeft: 8,
                marginTop: -50,
                borderRadius: 14,
                background: 'red',
                color: 'white'
            };
            return <div style={labelStyle}>{this.props.label}</div>;
        }
        return null;
    },
    render() {
        let isActive = this.isActive(this.props.route);
        let imageUrl = `/static/barista/img/sections${isActive ? '-active' : ''}/${this.props.route}.png`;
        let style,
            linkStyle = {
                textAlign: 'center',
                textDecoration: 'none',
                color: isActive ? '#65A329' : '#666666',
                position: 'relative'
            };
        if (this.props.horizontal) {
            style = {
                display: 'table',
                width: '100%',
                height: '20%'
            };
            assign(linkStyle, {
                display: 'table-cell',
                height: '100%',
                verticalAlign: 'middle'
            });
        } else {
            style = {
                float: 'left',
                width: '20%'
            };
            assign(linkStyle, {
                display: 'block'
            });
        }
        return <div style={style}>
            <Link to={this.props.route} style={linkStyle}>
                <img src={imageUrl} width={60}/>
                <div>{this.props.text}</div>
                {this._renderLabel()}
            </Link>
        </div>;
    }
});

const Nav = React.createClass({
    render() {
        let isHorizontal = this.props.horizontal;
        let style = {
            position: 'fixed',
            background: '#eeeeee',
            zIndex: 1
        };
        Object.assign(style,
            isHorizontal ? {
                top: 64,
                bottom: 0,
                width: 100
            } : {
                top: 64,
                left: 0,
                right: 0,
                paddingTop: 16
            });
        return <div style={style}>
            <NavItem horizontal={isHorizontal} route='current'  text='Заказы'    label={this.props.orderCount}/>
            <NavItem horizontal={isHorizontal} route='delivery' text='Доставка'  label={this.props.deliveryCount}/>
            <NavItem horizontal={isHorizontal} route='history'  text='История'/>
            <NavItem horizontal={isHorizontal} route='returns'  text='Отмененные'/>
            <NavItem horizontal={isHorizontal} route='stoplist' text='Стоп-лист'/>
        </div>
    }
});
export default Nav;
