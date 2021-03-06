from django.shortcuts import render
from scraper.scrape import Scrape
from Server import settings
from django.http import HttpResponse, HttpResponseBadRequest
from FreeRoomFinderServer.models import RoomBookedSlot, Room, Tag
import datetime
import re
from scraper.empty import Empty, EmptyRooms
import json


def refresh(request):
    Scrape.register_all_subjects_in_semester(university="ubc", year=2018, semester="Fall", campus="Vancouver")
    return HttpResponse("Success")

def main(request):
    return render(request, "FreeRoomFinderServer/main.html", context=None)

def db(request):
    db_path = settings.DATABASES["default"]["NAME"]
    with open(db_path, mode="rb") as f:
        response = HttpResponse(f, content_type='application/sql')
        response['Content-Disposition'] = 'attachment; filename="room_schedule.sqlite"'
        return response

def api(request):
    search_term = request.GET.get("search", "")
    if not search_term:
        return HttpResponseBadRequest("Missing 'search' parameter")
    if search_term == "empty":  # get empty classrooms

        # get the time
        time = request.GET.get("time", "")
        if not time:
            time = datetime.datetime.now().time()
        elif re.match(r"(\d{1}|\d{2}):\d{2}(|:\d{2})", time):
            split = time.split(":")
            time = datetime.time(hour=int(split[0]), minute=int(split[1]))
        else:
            return HttpResponseBadRequest("Malformed 'time' parameter, must be HH:MM or HH:MM:SS")

        # get the weekday
        weekday = request.GET.get("weekday", "")
        if not weekday:
            weekday = datetime.datetime.now().strftime("%A")  # today's day of the week
        elif weekday in Scrape.day_conversion:
            weekday = Scrape.day_conversion[weekday]
        elif weekday in Scrape.day_conversion.values():
            pass
        else:
            return HttpResponseBadRequest("Malformed 'weekday' parameter, must be in the form 'M' or 'Monday'")

        # set the year
        year = datetime.datetime.now().year
        year = 2018

        # semester
        month = datetime.datetime.now().month
        if month <= 4:
            semester = "Winter"
        elif month <= 8:
            semester = "Summer"
        else:
            semester = "Fall"

        # University
        university = request.GET.get("university", "")

        empty_rooms: EmptyRooms = Empty.find_empty(university=university,time=time, weekday=weekday, semester=semester, year=year)
        empty_rooms_json: str = json.dumps(empty_rooms, sort_keys=True, indent=4)
        return HttpResponse(empty_rooms_json)
