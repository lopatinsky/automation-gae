import { EventEmitter } from 'events';
import assign from 'object-assign';
import AppDispatcher from '../AppDispatcher';
import Actions from '../Actions';
import PersistenceMixin from '../utils/PersistenceMixin';

const MenuStore = assign({}, EventEmitter.prototype, PersistenceMixin, {
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
    startEditItem(itemId) {
        this.editing = {item: itemId};
        this.emit('change');
    },
    finishEditItem(editedItem) {
        let found = false;
        for (let cat of this.menu) {
            for (let item of cat.items) {
                if (item.id == editedItem.id) {
                    found = true;
                    assign(item, editedItem);
                    delete item._new;
                    break;
                }
            }
            if (found) break;
        }
        this.editing = null;
        this.emit('change');
    },
    cancelEdit() {
        if (this.menu[this.menu.length - 1]._new) {
            this.menu.pop();
        }
        for (let cat of this.menu) {
            if (cat.items.length && cat.items[cat.items.length - 1]._new) {
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
        this.editing = {item: item.id};
        this.emit('change');
    },
    startEditCategory(categoryId) {
        this.editing = {category: categoryId};
        this.emit('change');
    },
    finishEditCategory(editedCategory) {
        for (let cat of this.menu) {
            if (cat.id == editedCategory.id) {
                assign(cat, editedCategory);
                delete cat._new;
                break;
            }
        }
        this.editing = null;
        this.emit('change');
    },
    addCategory() {
        let category = this._createCategory();
        category._new = true;
        this.menu.push(category);
        this.editing = {category: category.id};
        this.emit('change');
    }
});
MenuStore.menu = [
    MenuStore._createCategory("Категория 1",
        MenuStore._createItem("Продукт 1", "Продукт 1 -- лучший в мире!", 50, "https://www.google.ru/images/srpr/logo11w.png"),
        MenuStore._createItem("Продукт 2", "Продукт 2 -- не лучший в мире :(", 50, "https://www.google.ru/images/srpr/logo11w.png")
    )
];
MenuStore.initPersistence(['menu', '_itemCounter', '_categoryCounter'], 'menu');
MenuStore.dispatchToken = AppDispatcher.register(action => {
    switch (action.actionType) {
        case Actions.ITEM_EDIT_STARTED:
            MenuStore.startEditItem(action.data);
            break;
        case Actions.ITEM_EDIT_FINISHED:
            MenuStore.finishEditItem(action.data);
            break;
        case Actions.EDIT_CANCELED:
            MenuStore.cancelEdit();
            break;
        case Actions.ITEM_ADDED:
            MenuStore.addItem(action.data);
            break;
        case Actions.CATEGORY_EDIT_STARTED:
            MenuStore.startEditCategory(action.data);
            break;
        case Actions.CATEGORY_EDIT_FINISHED:
            MenuStore.finishEditCategory(action.data);
            break;
        case Actions.CATEGORY_ADDED:
            MenuStore.addCategory();
            break;
        case Actions.RESTART:
            MenuStore.clearPersistence();
            break;
        case Actions.POST_TO_SERVER_SUCCESS:

    }
});

export default MenuStore;
