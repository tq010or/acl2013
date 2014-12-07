
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

var TIMEOUT = 30000;
var REPORT_SIZE = 20;
var last_time_stamp = null;
var wc_settings = null;
var prev_sname = null;

$(document).ready(function(){
    init();
});

//add a new end with function
String.prototype.endswith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

function init(){
    set_tab_status();
    bind_geolocate();
    set_init_controls();
    set_map();
}

function set_init_controls(){
    $(document).ajaxComplete(function(){
        $(".pred_result").text("");
    });
    wc_settings = {
        "size" : {
            "grid" : 1, // word spacing, smaller is more tightly packed
            "factor" : 0, // font resize factor, 0 means automatic
            "normalize" : false// reduces outliers for more attractive output
        },
        "options" : {
            "rotationRatio" : 0.5,// 0 is all horizontal, 1 is all vertical
            "color" : "random-dark",
            "printMultiplier" : 1,
            "sort" : "lowest"
        },
        "font" : "Futura, Helvetica, sans-serif",
        "shape" : "square"
    }
}

function unbind_report(){
    clearTimeout(timer);
}

function unbind_report(){
    clearTimeout(timer);
}

function bind_report(){
    $.post('/report', 
            {last_time_stamp: last_time_stamp},
            function(data, textStatus){
                result_json = data;
                json_obj = JSON.parse(data);
                if (json_obj["sname"] != prev_sname){
                    prev_sname = json_obj["sname"]
                    last_time_stamp = json_obj["last_time_stamp"];
                    summary = json_obj["summary"];
                    var li_num = $('#report_list').length;
                    if ( li_num > REPORT_SIZE) 
                        $("#report_list li").first().remove();
                    $("#report_list").prepend(
                            $('<li>').html(last_time_stamp + summary)
                            );
                    var accuracy = (json_obj["correct"] / (json_obj["correct"] + json_obj["wrong"]));
                    var result = "Correct predictions: " + json_obj["correct"] + "</br>Incorrect predictions: " + json_obj["wrong"] + "</br>Accuracy: " + Number(accuracy.toFixed(4));
                    $('#report_result').html(result);
                    update_markers(result_json);
                }
                timer = setTimeout(bind_report, TIMEOUT);
            });
}


function gen_word_cloud(wc_id, result_id, json_obj){
    $(result_id).html(json_obj["summary"]);
    var liw_dict = json_obj["liw"];
    $(wc_id).html("");
    for ( var w in liw_dict){
        $(wc_id).append("<span data-weight=" + liw_dict[w] + ">" + w + "</span>");
    }
    $(wc_id).awesomeCloud( wc_settings );
}

function bind_geolocate(){
    result_json = null;
    $("#text_submit").bind('click', function(){
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
                            gen_word_cloud("#text_wc", "#text_result", json_obj);
                            update_markers(result_json);
                        }
                    }else{
                        $('#text_result').text(info_dict["REST"]);
                    }
                });
    });
    $("#user_submit").bind('click', function(){
        $('#user_result').text(info_dict["BUSY"]);
        $.post('/user', 
                {user: $("#user_input").val()},
                function(data, textStatus){
                    result_json = data;
                    if( result_json != null ) {
                        json_obj = JSON.parse(result_json);
                        if ( json_obj["error"] ){
                            $('#user_result').text(json_obj["error"]);
                        }else{
                            gen_word_cloud("#user_wc", "#user_result", json_obj);
                            update_markers(result_json);
                        }
                    }else{
                        $('#user_result').text(info_dict["REST"]);
                    }
                });
    });
    $("#user_input").keyup(function(event){
        if(event.keyCode == 13){
            $("#user_submit").click();
            event.preventDefault();
        }
    });
    $("#text_input").keyup(function(event){
        if(event.keyCode == 13){
            $("#text_submit").click();
            event.preventDefault();
        }
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
            bounds.push([lat, lon]);
            marker_dict[i] = new L.Marker(
                    [lat, lon], {
                        icon: new number_icon({number: i + 1})
                    }).bindPopup(text).addTo(map);
        }
    }
    var pred_lat = json_obj['plat']
    var pred_lon = json_obj['plon']

    var summary = null;
    if (json_obj["tweets"]){
        var tweets = json_obj["tweets"];
        summary = "The most recent <b>" + tweets.length + "</b> tweets: </br>"
        for (i = 0; i < tweets.length; ++i){
            summary += (i + 1 + ": " + tweets[i] + "</br>");
        }
    }else{
        summary = "The predicted city is: " + json_obj['pc'];
    }

    bounds.push([pred_lat, pred_lon]);
    marker_dict["pred"] = new L.Marker(
            [pred_lat, pred_lon], {
                icon: new pred_icon()
            }).bindPopup(summary).addTo(map);
    map.fitBounds(bounds);
    console.log("create markers done");
}

function update_markers(result_json){
    //console.log(result_json);
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
            //remove_markers();
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
