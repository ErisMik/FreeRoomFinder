from FreeRoomFinderServer.models import BookingCache, Room, RoomBookedSlot
from scraper.scrape import Scrape


def delete_cache():
    """
    Delete all cached merged bookings. Does not affect RoomBookedSlot and Room data
    :return: None
    """
    BookingCache.objects.all().delete()


def create_cache():
    # list all session properties; we will iterate over this to get concurrent sessions
    start_times = set()
    end_times = set()
    years = set()
    semesters = set()
    weekdays = set()
    rooms = set()

    for booking in RoomBookedSlot.objects.all():
        start_times.add(booking.start_time)
        end_times.add(booking.end_time)
        years.add(booking.year)
        semesters.add(booking.semester)
        weekdays.add(booking.weekday)
        rooms.add(booking.room)

    # iterate over properties and find concurrent sessions
    for start_time in start_times:
        for end_time in end_times:
            for year in years:
                for semester in semesters:
                    for weekday in weekdays:
                        for room in rooms:
                            concurrent = RoomBookedSlot.objects.filter(start_time=start_time, end_time=end_time,
                                                                       year=year, semester=semester,
                                                                       weekday=weekday, room=room)
                            occasion_names = set()  # We put these in a set because there are sometimes concurrent courses with the same name, for example PHYC 1190
                            for booking in concurrent:
                                occasion_names.add(booking.occasion)
                            name = "; ".join(occasion_names)
                            merged = BookingCache(start_time=start_time, end_time=end_time,
                                                  year=year, semester=semester,
                                                  weekday=weekday, room=room,
                                                  occasions=name)
                            merged.save()


def refresh_cache():
    delete_cache()
    create_cache()