import injectTapEventPlugin from "react-tap-event-plugin";
import _ from 'core-js';
injectTapEventPlugin();

let fontStyleLink = document.createElement("link");
fontStyleLink.rel = "stylesheet";
fontStyleLink.href = "http://fonts.googleapis.com/css?family=Roboto:300,400,500,700&subset=latin,cyrillic";
document.head.appendChild(fontStyleLink);

fontStyleLink = document.createElement("link");
fontStyleLink.rel = "stylesheet";
fontStyleLink.href = "https://fonts.googleapis.com/icon?family=Material+Icons";
document.head.appendChild(fontStyleLink);

export default null;
