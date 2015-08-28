const loadSymbol = Symbol("load"),
    saveSymbol = Symbol("save"),
    propsSymbol = Symbol("props"),
    keySymbol = Symbol("key");

const PersistenceMixin = {
    [propsSymbol]: null,
    [keySymbol]: null,
    initPersistence(props, key) {
        this[propsSymbol] = props;
        this[keySymbol] = key;

        const loaded = this[loadSymbol]();
        if (!loaded) {
            this[saveSymbol](); // save defaults
        }

        this.on('change', this[saveSymbol]);
    },
    clearPersistence() {
        localStorage.removeItem(this[keySymbol]);
    },
    [loadSymbol]() {
        const rawData = localStorage.getItem(this[keySymbol]);
        let data = null;
        try {
            data = JSON.parse(rawData);
        } catch (e) { }

        // integrity check
        if (data) {
            for (let prop of this[propsSymbol]) {
                if (! (prop in data)) {
                    data = null;
                    break;
                }
            }
        }

        if (data) {
            for (let prop of this[propsSymbol]) {
                this[prop] = data[prop];
            }
        }
        return !!data;
    },
    [saveSymbol]() {
        const data = {};
        for (let prop of this[propsSymbol]) {
            data[prop] = this[prop];
        }
        localStorage.setItem(this[keySymbol], JSON.stringify(data));
    }
};
export default PersistenceMixin;
