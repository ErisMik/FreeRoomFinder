var allBookingValues = [];
var bookingsList;
var xhr = new XMLHttpRequest();
xhr.open('GET', '/db', true);
xhr.responseType = 'arraybuffer';
xhr.onload = function () {
    var uInt8Array = new Uint8Array(this.response);
    var db = new SQL.Database(uInt8Array);
    // set year
    var year = new Date().getFullYear();
    // set semester
    var month = new Date().getMonth();
    var semester;
    if (month <= 4)
        semester = "Winter";
    else if (month <= 8)
        semester = "Summer";
    else
        semester = "Fall";
    console.log(semester);
    // get rooms and bookings from DB
    var rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    var bookings = db.exec("SELECT * FROM FreeRoomFinderServer_roombookedslot WHERE year='" + year + "' AND semester='" + semester + "'");
    // create booking list data
    for (var i = 0; i < bookings[0].values.length; i++) {
        var b = bookings[0].values[i];
        var room_raw = rooms[0].values[b[7]];
        if (room_raw == undefined)
            continue;
        var room = room_raw[1] + " " + room_raw[2] + " " + room_raw[3];
        allBookingValues.push({
            year: b[1],
            semester: b[2],
            weekday: b[3],
            starttime: b[4],
            endtime: b[5],
            subject: b[6],
            room: room,
        });
    }
    // set up sorting
    var options = {
        valueNames: ["room", "subject", "starttime", "endtime", "weekday", "year", "semester"],
        item: '<li><h3 class="room"></h3><p class="subject"</p><p class="starttime"></p><p class="endtime"></p></li>'
    };
    bookingsList = new List('bookinglist', options, []);
    refreshList();
};
xhr.send();
$("#day").change(refreshList);
$("#time").change(refreshList);
function refreshList() {
    // get time in HHMM format
    var time_split = $("#time").val().split(":");
    var time = parseInt(time_split[0] + "" + time_split[1]);
    // only show bookings for the current weekday and current time
    var values = [];
    var weekday = $("#day").val();
    bookingsList.clear();
    for (var i = 0; i < allBookingValues.length; i++) {
        var booking = allBookingValues[i];
        var starttime_split = booking.starttime.split(":");
        var starttime = parseInt(starttime_split[0] + "" + starttime_split[1]);
        var endtime_split = booking.endtime.split(":");
        var endtime = parseInt(endtime_split[0] + "" + endtime_split[1]);
        if (allBookingValues[i].weekday == weekday /*&& starttime <= time && time <= endtime*/) {
            bookingsList.add(allBookingValues[i]);
        }
    }
}
// set up time picker
$('#time').timepicker({ timeFormat: "H:i" });
$('#timenow').on('click', function () {
    $('#time').timepicker('setTime', new Date());
});
