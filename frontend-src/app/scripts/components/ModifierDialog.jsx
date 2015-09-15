import React from 'react';
import { Dialog} from 'material-ui';

const ModifierDialog = React.createClass({
    render() {
        var modifier = this.props.modifier;
        return <Dialog
                    title={modifier.title} />;
    }
});

export default ModifierDialog;