import React from 'react';
import { Navbar, Grid, Row, Col } from 'react-bootstrap';
import { RouteHandler } from 'react-router';

const App = React.createClass({
    render() {
        return (
            <div>
                <Navbar staticTop brand="Ru-Beacon"/>

                <Grid>
                    <RouteHandler/>
                </Grid>
            </div>
            );
    }
});
export default App;
