import injectTapEventPlugin from "react-tap-event-plugin";
import _ from 'core-js';
injectTapEventPlugin();

const fontStyleLink = document.createElement("link");
fontStyleLink.rel = "stylesheet";
fontStyleLink.href = "http://fonts.googleapis.com/css?family=Roboto:300,400,500,700&subset=latin,cyrillic";
document.head.appendChild(fontStyleLink);
