/**
 * iot icon UI
 */
var number_icon = L.Icon.extend({
    options: {
        number: '',
        iconAnchor: [0, 0],
        className: 'leaflet-marker-icon'
    },
    createIcon: function () {
        var div = document.createElement('span');
        var img = this._createImg("static/img/marker-hole.png");
        var numdiv = document.createElement('span');
        numdiv.setAttribute ( "class", "number" );
        numdiv.innerHTML = this.options['number'] || '';
        div.appendChild ( img );
        div.appendChild ( numdiv );
        this._setIconStyles(div, 'icon');
        return div;
    },
});

var pred_icon = L.Icon.extend({
    options: {
        iconAnchor: [0, 0],
        className: 'leaflet-marker-icon'
    },
    createIcon: function () {
        var div = document.createElement('span');
        var img = this._createImg("static/img/marker-pred.png");
        div.appendChild ( img );
        this._setIconStyles(div, 'icon');
        return div;
    },
});
