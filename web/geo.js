var pc_iw = null; //info window to show user tweets
var oc_iw_list = []; //info window to show user tweets
var google_map = null; //the Google map object
var pc_marker = null; // predicted location
var oc_marker_list = []; // a list of oracvle locations: footprints

$(document).ready(function(){
        var myOptions = {
            zoom: 2,
            center: new google.maps.LatLng(10, 0),
            mapTypeId: google.maps.MapTypeId.ROADMAP
            };
        google_map = new google.maps.Map(document.getElementById("canvas"),  myOptions);
        google.maps.event.addListener(google_map, "click",
            function(){
                if(pc_iw){
                    pc_iw.close();
                }
                pc_iw = null;
                for(var i = 0; i < oc_iw_list.length; ++i)
                {
                   oc_iw_list[i].close();
                   oc_iw_list[i] = null;
                }
                oc_iw_list = [];
            });

});

 

function createInfoWindow(oc_marker, text){
    return function(){ // avoid clousre issue, otherwise, only last value is stored.
        for(var i = 0; i < oc_iw_list.length; ++i)
        {
           oc_iw_list[i].close();
        }
        oc_iw_list = [];
        var oc_iw = new google.maps.InfoWindow();
        oc_iw.setContent(text);
        oc_iw.open(google_map, oc_marker);
        oc_iw_list.push(oc_iw);
    };
}


function createNewMarkers(gt_dict){
    // add predicted location marker
    var fullBounds = new google.maps.LatLngBounds();
    var p_point = new google.maps.LatLng(gt_dict["plat"], gt_dict["plon"]);
    fullBounds.extend(p_point);
    pc_marker = new google.maps.Marker({position: p_point});
    var tweets = gt_dict["tweets"];
    var summary = gt_dict["summary"];
    var my_html = summary + "</br></br>Here are some recent tweets:</br>";
    for(var i = 0; i < tweets.length; ++i)
    {
        my_html += (i+1) + ": " + tweets[i] + " </br>";
    }

    google.maps.event.addListener(pc_marker, 
                "click", 
                function(){
                    if (pc_iw){
                        pc_iw.close();
                        pc_iw = null;
                    }
                    pc_iw = new google.maps.InfoWindow();
                    pc_iw.setContent(my_html);
                    pc_iw.open(google_map, pc_marker);
                });
    pc_marker.setMap(google_map);

    // add oracle location markers indexed by numbers
    var footprints = gt_dict["footprints"];
    for (var i = 0; i < footprints.length; ++i)
    {
        var city = footprints[i][0];
        var lat = footprints[i][1];
        var lon = footprints[i][2];
        var text = footprints[i][3];
        var o_point = new google.maps.LatLng(lat, lon);
        fullBounds.extend(o_point);
        text = "Text: " + text + " </br> " + "Accurate location: " + lat + ", " + lon + "";
        var oc_marker = new google.maps.Marker(
            {
                position: o_point,
                //changing icons with parameters
                icon:'https://chart.googleapis.com/chart?chst=d_map_pin_letter&chld=' + (i + 1) + '|00E13C|000000'
            }
        );

        google.maps.event.addListener(oc_marker, 
                "click", 
                createInfoWindow(oc_marker, text)
        );
        oc_marker.setMap(google_map);
        oc_marker_list.push(oc_marker);
    }

    //refocus on predicted location
    if(footprints.length > 1)
    {
        google_map.fitBounds(fullBounds);
    }
    else
    {
        google_map.setZoom(12);
        google_map.setCenter(p_point);
    }
}


function clearMarkers(){
    if(pc_iw){
        pc_iw.close();
        pc_iw = null;
    }
    if(pc_marker){
        pc_marker.setMap(null);
        pc_marker = null;
    }

    for(var i = 0; i < oc_iw_list.length; ++i)
    {
       oc_iw_list[i].close();
    }
    oc_iw_list = [];
    for (var i = 0; i < oc_marker_list.length; ++i){
        oc_marker_list[i].setMap(null);
    }
    oc_marker_list = [];
}


function geolocate(){
    // clear previous results
    $("li").remove();
    $("#processing").show();
    $.ajax("/", { type: 'POST', data:$("input").val()}).done(function(data)
    {
        // do whatever you want with the unpacked JSON data that is returned.
        $("li").remove();
        var gt_dict = $.parseJSON(data);
        var gt_error = gt_dict["error"];
        if(gt_error == null)
        {
            //debug
            //var tmp = "";
            //for(var k in gt_dict)
            //{
            //    tmp += k + ": " + gt_dict[k] +" \n";
            //}
            //alert(tmp);

            var gt_pc = gt_dict["pc"];
            var gt_plat = gt_dict["plat"];
            var gt_plon = gt_dict["plon"];
            var gt_sname = gt_dict["sname"];
            // update predicted results
            $("#res").append("<li> Prediction for <b>" + gt_sname + "<b>: <b>" + gt_pc + "</b>. (Latitude: <b>" + gt_plat + "</b>, Longitude: <b>" + gt_plon + "</b>) </li>");
            $("#res").append("<li>" + gt_dict["summary"] + "</li>");
            // remove old markers
            clearMarkers();
            // add new markers
            createNewMarkers(gt_dict);
        }
        else
        {
            $("#res").append("<li>Information: " + gt_error  + "</li>");
            clearMarkers();
        }
        $("#processing").hide();
    });
};

