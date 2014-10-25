
var map = null;
var result_json = null;
var marker_dict = {};

$(document).ready(function(){
    set_tab_status();
    set_map();
    bind_geolocate();
    bind_report();
});

function bind_report(){
    //TODO: perodically query server for results
    //
}

function bind_geolocate(){
    result_json = null;
    $("#text_submit").bind('click', function(){
        console.log($("#text_input").val());
        $.post('/text', 
                {text: $("#text_input").val()},
                function(data, textStatus){
                    result_json = data;
                    if( result_json != null ) 
                        update_results(result_json);
                });
    });
    $("#user_submit").bind('click', function(){
        console.log($("#user_input").val());
        $.post('/user', 
                {user: $("#user_input").val()},
                function(data, textStatus){
                    result_json = data;
                    if( result_json != null ) 
                        update_results(result_json);
                });
    });
}

function remove_markers(){
    console.log("remove markers");
    for( var key in marker_dict ){
        map.removeLayer(marker_dict[key]);
    }
    console.log("remove markers done");
}

function create_markers(){
    console.log("create markers");
    var bounds = [];
    var json_obj = JSON.parse(result_json);
    var footprints = json_obj['footprints'];
    if (footprints != undefined){
        for( var i = 0; i < footprints.length; ++i ){
            var city = footprints[i][0];
            var lat = footprints[i][1];
            var lon = footprints[i][2];
            var text = footprints[i][3];
            text = "Text: " + text + " </br> " + "Accurate location: " + lat + ", " + lon + "";
            console.log(text);
            bounds.push([lat, lon]);
            marker_dict[i] = new L.Marker(
                    [lat, lon], {
                        icon: new number_icon({number: i + 1})
                    }).bindPopup(text).addTo(map);
        }
    }
    var pred_lat = json_obj['plat']
    var pred_lon = json_obj['plon']
    var summary = "Predicted city is: " + json_obj['pc']
    bounds.push([pred_lat, pred_lon]);
    marker_dict["pred"] = new L.Marker(
            [pred_lat, pred_lon], {
                icon: new pred_icon()
            }).bindPopup(summary).addTo(map);
    map.fitBounds(bounds);
    console.log("create markers done");
}

function update_results(result_json){
    // clear existing results
    remove_markers();
    // add new results on the map
    create_markers();
}

function set_map(){
    map = L.map('map').setView([-37.8, 144.9], 11);
    L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
            maxZoom: 15,
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
                '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
                'Imagery © <a href="http://mapbox.com">Mapbox</a>',
            id: 'examples.map-i875mjb7'
        }).addTo(map);
}

function set_tab_status(){
    $('ul.tabs').each(function(){
        // For each set of tabs, we want to keep track of
        // which tab is active and it's associated content
        var $active, $content, $links = $(this).find('a');

        // If the location.hash matches one of the links, use that as the active tab.
        // If no match is found, use the first link as the initial active tab.
        $active = $($links.filter('[href="'+location.hash+'"]')[0] || $links[0]);
        $active.addClass('active');

        $content = $($active[0].hash);

        // Hide the remaining content
        $links.not($active).each(function () {
            $(this.hash).hide();
        });

        // Bind the click event handler
        $(this).on('click', 'a', function(e){
            // Make the old tab inactive.
            $active.removeClass('active');
            $content.hide();

            // Update the variables with the new link and content
            $active = $(this);
            $content = $(this.hash);

            // Make the tab active.
            $active.addClass('active');
            $content.show();

            // Prevent the anchor's default click action
            e.preventDefault();
        });
    });

}
