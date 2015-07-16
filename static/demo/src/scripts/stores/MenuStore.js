import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';

const MenuStore = assign({}, EventEmitter.prototype, {
    _itemCounter: 0,
    _categoryCounter: 0,
    _createItem(title, description, price, imageUrl) {
        return {
            id: ++ this._itemCounter,
            title, description, price, imageUrl
        }
    },
    _createCategory(title, ...items) {
        return {
            id: ++ this._categoryCounter,
            title, items
        }
    },

    menu: [],
    addChangeListener(fn) {
        this.on('change', fn);
    },
    removeChangeListener(fn) {
        this.removeListener('change', fn);
    },
    getCategories() {
        return this.menu;
    },

    editing: null,
    startEdit(itemId) {
        this.editing = itemId;
        this.emit('change');
    },
    finishEdit(editedItem) {
        let found = false;
        for (let cat of this.menu) {
            for (let item of cat.items) {
                if (item.id == editedItem.id) {
                    found = true;
                    assign(item, editedItem);
                    break;
                }
            }
            if (found) break;
        }
        this.editing = null;
        this.emit('change');
    },
    cancelEdit() {
        for (let cat of this.menu) {
            if (cat.items[cat.items.length - 1]._new) {
                cat.items.pop();
                break;
            }
        }
        this.editing = null;
        this.emit('change');
    },
    addItem(categoryId) {
        let category;
        for (let cat of this.menu) {
            if (cat.id == categoryId) {
                category = cat;
                break;
            }
        }
        let item = MenuStore._createItem();
        item._new = true;
        category.items.push(item);
        this.editing = item.id;
        this.emit('change');
    }
});
MenuStore.menu = [
    MenuStore._createCategory("Категория 1",
        MenuStore._createItem("Продукт 1", "Продукт 1 -- лучший в мире!", 50, "https://www.google.ru/images/srpr/logo11w.png"),
        MenuStore._createItem("Продукт 2", "Продукт 2 -- не лучший в мире :(", 50, "https://www.google.ru/images/srpr/logo11w.png")
    )
];
MenuStore.dispatchToken = AppDispatcher.register(action => {
    switch (action.actionType) {
        case Actions.EDIT_STARTED:
            MenuStore.startEdit(action.data);
            break;
        case Actions.EDIT_FINISHED:
            MenuStore.finishEdit(action.data);
            break;
        case Actions.EDIT_CANCELED:
            MenuStore.cancelEdit();
            break;
        case Actions.ITEM_ADDED:
            MenuStore.addItem(action.data);
            break;
    }
});

export default MenuStore;
