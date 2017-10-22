let allBookingValues = [];
let bookingsList;

let xhr = new XMLHttpRequest();
xhr.open('GET', '/db', true);
xhr.responseType = 'arraybuffer';
xhr.onload = function () {
    let uInt8Array = new Uint8Array(this.response);
    let db = new SQL.Database(uInt8Array);

    // set year
    let year = new Date().getFullYear();

    // set semester
    let month = new Date().getMonth();
    let semester;
    if (month <= 4) semester = "Winter";
    else if (month <= 8) semester = "Summer";
    else semester = "Fall";
    console.log(semester);

    // get rooms and bookings from DB
    let rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    let bookings = db.exec(`SELECT * FROM FreeRoomFinderServer_roombookedslot WHERE year='${year}' AND semester='${semester}'`);

    // create booking list data
    for (let i = 0; i < bookings[0].values.length; i++) {
        let b = bookings[0].values[i];
        let room_raw = rooms[0].values[b[7]];
        if (room_raw == undefined) continue;
        let room = `${room_raw[1]} ${room_raw[2]} ${room_raw[3]}`;
        allBookingValues.push({
            year: b[1],
            semester: b[2],
            weekday: b[3],
            starttime: b[4],
            endtime: b[5],
            subject: b[6],
            room: room,
        })
    }

    // set up sorting
    let options = {
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
    let time_split = $("#time").val().split(":");
    let time = parseInt(time_split[0] + "" + time_split[1]);

    // only show bookings for the current weekday and current time
    let values = [];
    let weekday = $("#day").val();
    bookingsList.clear();
    for (let i = 0; i < allBookingValues.length; i++) {
        let booking = allBookingValues[i];
        let starttime_split = booking.starttime.split(":");
        let starttime = parseInt(starttime_split[0] + "" + starttime_split[1]);
        let endtime_split = booking.endtime.split(":");
        let endtime = parseInt(endtime_split[0] + "" + endtime_split[1]);
        if (allBookingValues[i].weekday == weekday /*&& starttime <= time && time <= endtime*/){
            bookingsList.add(allBookingValues[i]);
        }
    }
}

// set up time picker
$('#time').timepicker({timeFormat: "H:i"});
$('#timenow').on('click', function () {
    $('#time').timepicker('setTime', new Date());
});