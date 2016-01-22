import React from 'react';
import { Link } from 'react-router';

const NavItem = React.createClass({
    contextTypes: {
        history: React.PropTypes.object
    },
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
                marginTop: -36,
                borderRadius: 14,
                background: 'red',
                color: 'white'
            };
            return <div style={labelStyle}>{this.props.label}</div>;
        }
        return null;
    },
    render() {
        let isActive = this.context.history.isActive(this.props.route);
        let imageUrl = `/static/barista/img/sections${isActive ? '-active' : ''}/${this.props.route}.png`;
        let style,
            linkStyle = {
                textAlign: 'center',
                textDecoration: 'none',
                color: isActive ? '#65A329' : '#666666'
            };
        if (this.props.horizontal) {
            style = {
                display: 'table',
                width: '100%',
                height: `${1.0 / this.props.itemCount * 100}%`
            };
            Object.assign(linkStyle, {
                display: 'table-cell',
                height: '100%',
                verticalAlign: 'middle'
            });
        } else {
            style = {
                display: 'table-cell',
                width: '1%'
            };
            Object.assign(linkStyle, {
                display: 'block'
            });
        }
        let imgDivStyle = {
            height: 60,
            width: 60,
            margin: '0 auto',
            position: 'relative',
            background: `url(${imageUrl})`,
            backgroundSize: 'contain'
        };
        return <div style={style}>
            <Link to={this.props.route} style={linkStyle}>
                <div style={imgDivStyle}>
                    {this._renderLabel()}
                </div>
                <div>{this.props.text}</div>
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
                display: 'table',
                tableLayout: 'fixed',
                top: 64,
                left: 0,
                width: '100%',
                paddingTop: 16
            });
        let navCount = 2; // history, returns -- stoplist is hidden atm
        if (this.props.showCurrent) { navCount += 1; }
        if (this.props.showDelivery) { navCount += 1; }
        return <div style={style}>
            {this.props.showCurrent &&
            <NavItem horizontal={isHorizontal} itemCount={navCount} route='current'  text='Заказы'    label={this.props.orderCount}/>}
            {this.props.showDelivery &&
            <NavItem horizontal={isHorizontal} itemCount={navCount} route='delivery' text='Доставка'  label={this.props.deliveryCount}/>}
            <NavItem horizontal={isHorizontal} itemCount={navCount} route='history'  text='История'/>
            <NavItem horizontal={isHorizontal} itemCount={navCount} route='returns'  text='Отмененные'/>
            {/*<NavItem horizontal={isHorizontal} itemCount={navCount} route='stoplist' text='Стоп-лист'/>*/}
        </div>
    }
});
export default Nav;
