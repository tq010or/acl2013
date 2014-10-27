
var map = null;
var result_json = null;
var json_obj = null;
var timer = null;
var marker_dict = {};

var info_dict = {
    "BUSY": "Prediction in progress ...",
    "REST": "REST result is null",
    "OTHER": "Unknown error"
};

var TIMEOUT = 5000;
var REPORT_SIZE = 1;
var last_time_stamp = null;

$(document).ready(function(){
    init();
    bind_geolocate();
});

//add a new end with function
String.prototype.endswith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

function init(){
    set_tab_status();
    set_init_controls();
    set_map();
}

function set_init_controls(){
    $(document).ajaxComplete(function(){
        $(".pred_result").text("");
    });
}

function unbind_report(){
    clearTimeout(timer);
}

function bind_report(){
    $.post('/report', 
            {last_time_stamp: last_time_stamp},
            function(data, textStatus){
                var report_obj = JSON.parse(data);
                last_time_stamp = report_obj["last_time_stamp"];
                //TODO: add pred results into lists
                var $items = $('#report_list').children();
                if ( $items.length > REPORT_SIZE) 
                    $items[$items.length - 1].remove();
                $("#report_list").prepend(
                        $('<li>').append(
                                $('<span>').append(last_time_stamp)
                                ));
                console.log(last_time_stamp);
                //TODO: update stats, using D3 or other visualisation tools?
                timer = setTimeout(bind_report, TIMEOUT);
            });
}

function bind_geolocate(){
    result_json = null;
    $("#text_submit").bind('click', function(){
        console.log($("#text_input").val());
        $('#text_result').text(info_dict["BUSY"]);
        $.post('/text', 
                {text: $("#text_input").val()},
                function(data, textStatus){
                    result_json = data;
                    if( result_json != null ){
                        json_obj = JSON.parse(result_json);
                        if ( json_obj["error"] ){
                            $('#text_result').text(json_obj["error"]);
                        }else{
                            update_results(result_json);
                            $('#text_result').text(json_obj["pc"]);
                            //$('#text_result').text(json_obj["summary"]);
                        }
                    }else{
                        $('#text_result').text(info_dict["REST"]);
                    }
                });
    });
    $("#user_submit").bind('click', function(){
        console.log($("#user_input").val());
        $('#user_result').text(info_dict["BUSY"]);
        $.post('/user', 
                {user: $("#user_input").val()},
                function(data, textStatus){
                    result_json = data;
                    if( result_json != null ) {
                        json_obj = JSON.parse(result_json);
                        if ( json_obj["error"] ){
                            $('#user_busy').text(json_obj["error"]);
                        }else{
                            $('#user_result').text(json_obj["pc"]);
                            update_results(result_json);
                        }
                    }else{
                        $('#user_busy').text(info_dict["REST"]);
                    }
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
            remove_markers();
            // Make the old tab inactive.
            $active.removeClass('active');
            $content.hide();

            // Update the variables with the new link and content
            $active = $(this);
            $content = $(this.hash);

            // Make the tab active.
            $active.addClass('active');
            $content.show();

            // if report page is selected, bind the remote report endpoint
            if ( this.hash.endswith("#report") ){
                bind_report();
            }else{
                unbind_report();
            }

            // Prevent the anchor's default click action
            e.preventDefault();
        });
    });

}
