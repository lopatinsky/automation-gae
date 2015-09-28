import MobileDetect from 'mobile-detect';
import { Howler, Howl } from 'howler/howler.min';
import Actions from '../Actions';
import BaseStore from './BaseStore';

const detect = new MobileDetect(navigator.userAgent);

const SystemStore = new BaseStore({
    _sound: null,
    _initSound() {
        this._sound = new Howl({
            src: ["/static/barista/sounds/ship_horn.mp3"]
        });
    },
    init() {
        this._initSound();
    },
    playSound() {
        if (Howler._iOSEnabled !== false) { // true means enabled, undefined means non-iOS
            this._sound.play();
        }
    }
}, action => {
    switch (action.actionType) {
        case Actions.INIT_APP:
            SystemStore.init();
            break;
    }
});
export default SystemStore;
