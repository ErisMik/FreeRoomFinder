from FreeRoomFinderServer.models import Room, RoomBookedSlot
from typing import List, Dict, Union
import datetime

# define types
EmptyRooms = List[Dict[str, str]]


class Empty:
    """
    This class is designed to find empty rooms.
    """

    @staticmethod
    def serialize_time(time: datetime.time, seconds: bool = False) -> str:
        """
        Convert a time object to a string
        :param time: The time object to convert
        :param seconds: Whether to include seconds
        :return: The time as a string, HH:MM or HH:MM:SS
        """
        if not time:
            return "Never"
        if seconds:
            return "{:02d}:{:02d}:{:02d}".format(time.hour, time.minute, time.second)
        else:
            return "{:02d}:{:02d}".format(time.hour, time.minute)


    @staticmethod
    def serialize_room(room: Room) -> str:
        return "{} {} {}".format(room.campus, room.building, room.number)


    @staticmethod
    def find_empty(time: datetime.time, weekday: str, year: int, semester: str) -> EmptyRooms:
        """
        Find empty rooms at a given time on a given day in a given semester of a given year
        :param time: The current time
        :param weekday: The current weekday, written out in full (ex: Monday)
        :param year: The current year, four digits
        :param semester: The current semester, written out in full (ex: Fall)
        :return: A list of dicts, each containing an empty room, the end time of the previous class, and the start time of the next class.
        """
        empty_rooms: EmptyRooms = []
        for room in Room.objects.all():
            is_empty = True
            last_end_time: datetime.time = None  # end of the most recent class
            next_start_time: datetime.time = None  # beginning of the next class
            for booking in RoomBookedSlot.objects.filter(room=room, weekday=weekday, year=year, semester=semester):
                if booking.end_time < time:  # the booking is over
                    if not last_end_time or booking.end_time > last_end_time:
                        last_end_time = booking.end_time
                elif booking.start_time > time:  # the booking has yet to start
                    if not next_start_time or booking.start_time < next_start_time:
                        next_start_time = booking.start_time
                else:  # the booking is currently ongoing
                    is_empty = False
                    break
            if is_empty:
                empty_rooms.append({
                    "room": Empty.serialize_room(room),
                    "last_end_time": Empty.serialize_time(last_end_time),
                    "next_start_time": Empty.serialize_time(next_start_time)
                })
        return empty_rooms
