import React from 'react';
import { ButtonLink } from 'react-router-bootstrap';
import MenuCategory from './MenuCategory';
import MenuStore from '../stores/MenuStore';

const Step2 = React.createClass({
    getInitialState() {
        return {
            categories: MenuStore.getCategories(),
            edit: MenuStore.editing
        };
    },
    _onStoreChange() {
        this.setState({
            categories: MenuStore.getCategories(),
            edit: MenuStore.editing
        });
    },
    componentDidMount() {
        MenuStore.addChangeListener(this._onStoreChange)
    },
    componentWillUnmount() {
        MenuStore.removeChangeListener(this._onStoreChange);
    },
    render() {
        let categories = this.state.categories.map(category => {
            return <MenuCategory
                key={category.id}
                category={category}
                edit={this.state.edit}/>
        }) ;
        return <div>
            <h1>Настройка меню</h1>
            {categories}
        </div>;
    }
});
export default Step2;
