import React from 'react';
const YandexMapsAPI = window.ymaps;

const AddressPicker = React.createClass({
    componentDidMount() {
        YandexMapsAPI.ready(() => {
            const map = new YandexMapsAPI.Map(this.refs.map.getDOMNode(), {
                center: [55.76, 37.64],
                zoom: 12
            });
            map.events.add('click', this._onMapClick);
        });
    },
    render() {
        return <div ref='map' style={{height: '500px'}}/>
    },
    _onMapClick(e) {
        const map = e.get('map'),
            coords = e.get('coords');

        YandexMapsAPI.geocode(coords).then(res => {
            const firstObj = res.geoObjects.get(0),
                address = firstObj.properties.get('text');

            window['@@addressPicked'] = () => {
                console.log(coords);
                this.props.onPicked({
                    lat: coords[0],
                    lng: coords[1],
                    address
                });
            };

            const content = `<div>
                <strong>${firstObj.properties.get('text')}</strong><br/>
                <a href="#" onclick="window['@@addressPicked'](); return false;">Выбрать адрес</a>
            </div>`;
            map.balloon.open(coords, content);
        })
    }
});
export default AddressPicker;
