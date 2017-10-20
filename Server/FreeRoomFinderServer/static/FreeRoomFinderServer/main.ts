let xhr = new XMLHttpRequest();
xhr.open('GET', '/db', true);
xhr.responseType = 'arraybuffer';

xhr.onload = function () {
    let uInt8Array = new Uint8Array(this.response);
    let db = new SQL.Database(uInt8Array);
    let rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    let bookings = db.exec("SELECT * FROM FreeRoomFinderServer_roombookedslot");

    console.log(bookings)
};
xhr.send();