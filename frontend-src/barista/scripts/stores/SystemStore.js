import MobileDetect from 'mobile-detect';
import Actions from '../Actions';
import BaseStore from './BaseStore';

const detect = new MobileDetect(navigator.userAgent);

const SystemStore = new BaseStore({
    soundMayNotWork: false,

    _setSoundMayNotWork(value) {
        this.soundMayNotWork = value;
        this._changed();
    },

    _testWithEmptySound() {
        let timeout;
        soundManager.createSound({
            id: 'silence',
            url: '/static/barista/sounds/empty.mp3',
            autoPlay: true,
            onplay() {
                timeout = setTimeout(() => {
                    SystemStore._setSoundMayNotWork(true);
                }, 500);
            },
            onFinish() {
                clearTimeout(timeout);
                SystemStore._setSoundMayNotWork(false);
            }
        })
    },

    _initSound() {
        const ios = detect.os() == "iOS",
            android = detect.os() == "AndroidOS";
        soundManager.setup({
            url: '/static/barista/swf',
            //debugMode: false,
            forceUseGlobalHTML5Audio: ios,
            onready() {
                soundManager.createSound({
                    id: 'new_orders',
                    url: '/static/barista/sounds/ship_horn.mp3',
                    autoLoad: true
                });
                if (ios) {
                    SystemStore._setSoundMayNotWork(true);
                } else if (android) {
                    SystemStore._testWithEmptySound();
                }
            }
        });
    },
    init() {
        this._initSound();
    },
    testedSound() {
        this.soundMayNotWork = false;
        this._changed();
    }
}, action => {
    switch (action.actionType) {
        case Actions.INIT_APP:
            SystemStore.init();
            break;
        case Actions.TESTED_SOUND:
            SystemStore.testedSound();
            break;
    }
});
export default SystemStore;
