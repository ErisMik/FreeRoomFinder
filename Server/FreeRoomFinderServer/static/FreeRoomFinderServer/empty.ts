function HH_MM_SS_to_HH_MM(time: string): string {
    /**
     * Converts time from HH:MM:SS format to HH:MM format
     * @type {string[]}
     */
    let split = time.split(":");
    return split[0] + ":" + split[1];
}

let universityElement = $("#university");
let weekdayElement = $("#day");
let timeElement = $("#time");
let timeNowButton = $("#timenow");

let time: number;
let weekday: string;

let emptyList: List;
let emptyRooms: Array<Object>;

function init() {

    // set up event handlers
    universityElement.change(refreshList);
    weekdayElement.change(refreshList);
    timeElement.change(refreshList);

    // set up time picker
    timeElement.timepicker({timeFormat: "H:i"});

    // set time to now
    timeNowButton.on('click', function () {
        timeElement.timepicker('setTime', new Date());
    });
    timeNowButton.trigger("click");

    // set weekday to today
    let weekdayTable = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    let d = new Date().getDay();
    weekdayElement.val(weekdayTable[d]);

    // set up sorting
    let options = {
        valueNames: ["room", "next_start_time", "last_end_time"],
        item: '<tr><td class="room"></td><td class="last_end_time"></td><td class="next_start_time"</td></tr>'
    };

    // set up list
    emptyList = new List('emptylist', options, []);

    // refresh list
    refreshList();
}

function refreshList() {
    time = timeElement.val();
    weekday = weekdayElement.val();
    university = universityElement.val() 

    let xhr = new XMLHttpRequest();
    xhr.open('GET', `/api?search=empty&university=${university}&time=${time}&weekday=${weekday}`, true);
    xhr.responseType = 'arraybuffer';
    xhr.onload = function () {
        let decoded = String.fromCharCode.apply(null, new Uint8Array(this.response));
        emptyRooms = JSON.parse(decoded);

        emptyList.clear();
        emptyList.add(emptyRooms);
        emptyList.sort("room");

    };
    xhr.send();
}

init();