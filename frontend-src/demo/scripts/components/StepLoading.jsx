import React from 'react';
import Spinner from 'react-spinner';

const StepLoading = React.createClass({
    render() {
        return <div className="card-container">
            <h4 style={{textAlign: 'center'}}>Подождите, пожалуйста</h4>
            <Spinner style={{height: '60px', width: '60px', marginTop: '60px'}}/>
            <p className="lead" style={{textAlign: 'center'}}>
                Мы уже настраиваем Ваше приложение. Это займет не более минуты.
            </p>
        </div>;
    }
});
export default StepLoading;
