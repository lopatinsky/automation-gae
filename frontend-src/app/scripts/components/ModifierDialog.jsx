import React from 'react';
import { Dialog} from 'material-ui';
import { ModifierStore } from '../stores';

const ModifierDialog = React.createClass({
    render() {
        var modifier = ModifierStore.getModifier();
        return <Dialog
                    title={modifier.title} />;
    }
});

export default ModifierDialog;