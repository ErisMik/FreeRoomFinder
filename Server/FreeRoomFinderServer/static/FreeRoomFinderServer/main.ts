let xhr = new XMLHttpRequest();
xhr.open('GET', '/db', true);
xhr.responseType = 'arraybuffer';

let rooms;
let bookings;
let values = []

xhr.onload = function () {
    let uInt8Array = new Uint8Array(this.response);
    let db = new SQL.Database(uInt8Array);
    rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    bookings = db.exec("SELECT * FROM FreeRoomFinderServer_roombookedslot");
    for (let i = 0; i < bookings[0].values.length; i++) {
        let b = bookings[0].values[i];
        values.push({
            year: b[1],
            semester: b[2],
            weekday: b[3],
            starttime: b[4],
            endtime: b[5],
            subject: b[6],
            room: rooms[0].values[b[7]],
        })
    }

    console.log(bookings)
};
xhr.send();

$('#search').keyup(_.debounce(onSearch, 500));

function onSearch() {

}

// set up time picker
$('#time').timepicker({timeFormat: "H:i"});
$('#timenow').on('click', function () {
    $('#time').timepicker('setTime', new Date());
});


// set up sorting
let options = {
    valueNames: ["room", "subject", "starttime", "endtime", "weekday", "year", "semester"],
    item: '<li><h3 class="room"></h3><p class="subject"</p><p class="year"></p><p class="semester"></p><p class="starttime"></p><p class="endtime"></p><p class="weekday"></p></li>'
};

let userList = new List('bookinglist', options, values);