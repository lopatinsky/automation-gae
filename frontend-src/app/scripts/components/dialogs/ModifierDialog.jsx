import React from 'react';
import Dialog from 'material-ui/lib/dialog';
import ChoicesFragment from './ChoicesFragment';

const ModifierDialog = React.createClass({
    render() {
        let chosenChoice = null, title = '';
        if (this.props.modifier) {
            chosenChoice = this.props.chosenChoices[this.props.modifier.modifier_id];
            title = this.props.modifier.title;
        }
        return (
            <Dialog autoScrollBodyContent={true}
                    ref="modifierDialog"
                    open={this.props.open}
                    onRequestClose={this.props.requestClose}
                    title={title}>
                <ChoicesFragment modifier={this.props.modifier}
                                 chosen={chosenChoice}
                                 onChange={this.props.onChange}
                                 requestClose={this.props.requestClose}/>
            </Dialog>
        );
    }
});

export default ModifierDialog;