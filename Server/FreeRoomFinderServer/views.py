from django.shortcuts import render
from scraper.scrape import Scrape
from Server import settings
from django.http import HttpResponse, HttpResponseBadRequest
from FreeRoomFinderServer.models import RoomBookedSlot, Room, Tag
import datetime
import re
from scraper.empty import Empty, EmptyRooms
import json


"""def refresh(request):
    Scrape.register_all_subjects_in_semester(year=2017, semester=1, campus="Vancouver")
    return HttpResponse("Success")"""


"""def partial_refresh(request):
    Scrape.register_all_pages_in_subject(subject="ANAT", year=2017, semester="Fall", campus="Halifax")
    return HttpResponse("Success")"""


def db(request):
    db_path = settings.DATABASES["default"]["NAME"]
    with open(db_path, mode="rb") as f:
        response = HttpResponse(f, content_type='application/sql')
        response['Content-Disposition'] = 'attachment; filename="room_schedule.sqlite"'
        return response


def bookings(request):
    return render(request, "FreeRoomFinderServer/main.html", context=None)


def api(request):
    Scrape.register_all_subjects_in_semester(year=2017, semester=1, campus="Vancouver")
    
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

        # semester
        month = datetime.datetime.now().month
        if month <= 5:
            semester = 2
        else:
            semester = 1

        empty_rooms: EmptyRooms = Empty.find_empty(time=time, weekday=weekday, semester=semester, year=year)
        empty_rooms_json: str = json.dumps(empty_rooms, sort_keys=True, indent=4)
        return HttpResponse(empty_rooms_json)


def empty(request):
    """
    A page that shows empty rooms
    :param request: 
    :return: 
    """
    return render(request, "FreeRoomFinderServer/empty.html", context=None)