import ThemeManager from 'material-ui/lib/styles/theme-manager';
import LightRawTheme from 'material-ui/lib/styles/raw-themes/light-raw-theme';
import settings from './settings';

const lightMuiTheme = ThemeManager.getMuiTheme(LightRawTheme);
const palette = {
    primary1Color: settings.primaryColor,
    primary2Color: settings.primaryColor,
    primary3Color: settings.primaryColor,
    accent1Color: settings.primaryColor,
    accent2Color: settings.primaryColor,
    accent3Color: settings.primaryColor
};

export default ThemeManager.modifyRawThemePalette(lightMuiTheme, palette);
