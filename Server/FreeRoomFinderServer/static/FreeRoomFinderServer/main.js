var xhr = new XMLHttpRequest();
xhr.open('GET', '/db', true);
xhr.responseType = 'arraybuffer';
xhr.onload = function () {
    var uInt8Array = new Uint8Array(this.response);
    var db = new SQL.Database(uInt8Array);
    var rooms = db.exec("SELECT * FROM FreeRoomFinderServer_room");
    var bookings = db.exec("SELECT * FROM FreeRoomFinderServer_roombookedslot");
    console.log(bookings);
};
xhr.send();
