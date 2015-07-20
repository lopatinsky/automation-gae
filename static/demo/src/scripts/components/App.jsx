import React from 'react';
import { Navbar, Grid, Row, Col } from 'react-bootstrap';
import Step1 from './Step1';
import Step2 from './Step2';
import Step3 from './Step3';
import StepLoading from './StepLoading';
import StepFinish from './StepFinish';
import ProgressStore from '../stores/ProgressStore';

const App = React.createClass({
    contentTypes: {
        [ProgressStore.steps.INFO]: Step1,
        [ProgressStore.steps.MENU]: Step2,
        [ProgressStore.steps.VENUE]: Step3,
        [ProgressStore.steps.LOADING]: StepLoading,
        [ProgressStore.steps.FINISH]: StepFinish
    },
    getInitialState() {
        return {step: ProgressStore.getStep()};
    },
    _onStoreChange() {
        this.setState({step: ProgressStore.getStep()});
    },
    componentDidMount() {
        ProgressStore.addChangeListener(this._onStoreChange);
    },
    componentWillUnmount() {
        ProgressStore.removeChangeListener(this._onStoreChange);
    },
    render() {
        const Content = this.contentTypes[this.state.step];
        return (
            <div>
                <Navbar staticTop brand="Ru-Beacon"/>

                <Grid>
                    <Content/>
                </Grid>
            </div>
            );
    }
});
export default App;
