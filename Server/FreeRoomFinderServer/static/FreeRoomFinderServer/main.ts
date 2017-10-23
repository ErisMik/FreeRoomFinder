function HH_MM_SS_to_HH_MM(time : string): string {
    /**
     * Converts time from HH:MM:SS format to HH:MM format
     * @type {string[]}
     */
    let split = time.split(":");
    return split[0] + ":" + split[1];
}

let allBookingValues = [];
let bookingsList;
let rooms;
let bookings;

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
    rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    bookings = db.exec(`SELECT * FROM FreeRoomFinderServer_roombookedslot WHERE year='${year}' AND semester='${semester}'`);

    // create booking list data
    for (let i = 0; i < bookings[0].values.length; i++) {
        let b = bookings[0].values[i];
        let room_raw = db.exec(`SELECT * FROM FreeRoomFinderServer_room WHERE id=${b[7]}`)[0]["values"][0];
        if (room_raw == undefined) continue;
        let room = `${room_raw[1]} ${room_raw[2]} ${room_raw[3]}`;
        allBookingValues.push({
            year: b[1],
            semester: b[2],
            weekday: b[3],
            starttime: HH_MM_SS_to_HH_MM(b[4]),
            endtime: HH_MM_SS_to_HH_MM(b[5]),
            subject: b[6],
            room: room,
        })
    }

    // set up sorting
    let options = {
        valueNames: ["room", "subject", "starttime", "endtime", "weekday", "year", "semester"],
        item: '<tr><td class="room"></td><td class="subject"</td><td class="starttime"></td><td class="endtime"></td></tr>'
    };

    bookingsList = new List('bookinglist', options, []);

    refreshList();
};

xhr.send();

$("#day").change(refreshList);
/*$("#time").change(refreshList);*/


function refreshList(): void {
    // only show bookings for the current weekday
    let values = [];
    let weekday = $("#day").val();
    bookingsList.clear();
    let valuesToAdd = [];
    for (let i = 0; i < allBookingValues.length; i++) {
        let booking = allBookingValues[i];
        if (allBookingValues[i].weekday == weekday){
            valuesToAdd.push(allBookingValues[i]);
        }
    }
    bookingsList.add(valuesToAdd);
    bookingsList.sort("starttime");

}

// set up time picker
/*$('#time').timepicker({timeFormat: "H:i"});
$('#timenow').on('click', function () {
    $('#time').timepicker('setTime', new Date());
});*/