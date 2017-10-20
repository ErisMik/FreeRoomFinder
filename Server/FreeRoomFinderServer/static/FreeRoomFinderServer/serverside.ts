/**
 * This file is used for the page that uses serverside search.
 */

$('#search').keyup(_.debounce(onSearch, 500));

function onSearch() {
    let searchVal = $("#search").value;
    let xhr = new XMLHttpRequest();
    xhr.open('GET', `/api?search=${searchVal}`, true);
    xhr.responseType = 'arraybuffer';

    xhr.onload = function () {
        let uInt8Array = new Uint8Array(this.response);
        let db = new SQL.Database(uInt8Array);
        let rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
        let bookings = db.exec("SELECT * FROM FreeRoomFinderServer_roombookedslot");

        console.log(bookings)
    };
    xhr.send();
}