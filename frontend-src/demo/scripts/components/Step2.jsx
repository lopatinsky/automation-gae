import React from 'react';
import { Button, Glyphicon } from 'react-bootstrap';
import MenuCategory from './MenuCategory';
import MenuStore from '../stores/MenuStore';
import ProgressStore from '../stores/ProgressStore';
import Actions from '../Actions';

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
        });
        let addCard = this.state.categories[this.state.categories.length - 1]._new ? null :
            <div className="card">
                <div>
                    <Button onClick={this._add} disabled={this.state.edit !== null}>
                        <Glyphicon glyph='plus'/> Добавить категорию
                    </Button>
                </div>
            </div>;
        return <div>
            <h3>Настройка меню</h3>
            <div className="cards-container">
                {categories}
                {addCard}
                <div>
                    <Button onClick={this._onPrevClick}>Назад</Button>
                    <Button bsStyle='primary' onClick={this._onNextClick} className="pull-right">Далее</Button>
                </div>
            </div>
        </div>;
    },
    _onNextClick() {
        Actions.goToStep(ProgressStore.steps.VENUE);
    },
    _onPrevClick() {
        Actions.goToStep(ProgressStore.steps.INFO);
    },
    _add() {
        Actions.addCategory();
    }
});
export default Step2;
