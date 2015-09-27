import { Styles } from 'material-ui';
const { Colors, ThemeManager, LightRawTheme } = Styles;

const lightMuiTheme = ThemeManager.getMuiTheme(LightRawTheme);
const palette = {
    primary1Color: Colors.lightGreen500,
    primary2Color: Colors.lightGreen700,
    primary3Color: Colors.lightGreen100,
    accent1Color: Colors.pinkA200,
    accent2Color: Colors.pinkA400,
    accent3Color: Colors.pinkA100,
};
export default ThemeManager.modifyRawThemePalette(lightMuiTheme, palette);
