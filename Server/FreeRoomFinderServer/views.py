from django.shortcuts import render
from scraper.scrape import Scrape
from Server import settings
from django.http import HttpResponse
from FreeRoomFinderServer.models import RoomBookedSlot, Room, Tag


def refresh(request):
    Scrape.register_all_subjects_in_semester(year=2017, semester="Fall", campus="Halifax")
    return "Success"


def db(request):
    db_path = settings.DATABASES["default"]["NAME"]
    with open(db_path, mode="rb") as f:
        response = HttpResponse(f, content_type='application/sql')
        response['Content-Disposition'] = 'attachment; filename="room_schedule.sql"'
        return response


def main(request):
    return render(request, "FreeRoomFinderServer/main.html", context=None)


def api(request):
    search_term = request.GET.get("search", "")
    if not search_term:
        return None
    matching_rooms = Room.objects.filter()