from django.db import models


class Room(models.Model):
    """
    A single room on a campus
    """
    campus = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    number = models.CharField(max_length=100)  # some room numbers have letters in them
    capacity = models.IntegerField(default=0)  # can guess this from max class sizes

    class Meta:
        unique_together = ("campus", "building", "number")


class RoomBookedSlot(models.Model):
    """
    A single booking for a room
    """
    year = models.IntegerField(default=0)  # no sense using a date here
    semester = models.CharField(max_length=10)  # "Fall", "Winter", or "Summer"
    weekday = models.CharField(max_length=10)  # "Monday", "Tuesday", etc
    start_time = models.TimeField()
    end_time = models.TimeField()
    occasion = models.CharField(max_length=1000)  # typically a course name and number, but leave it broad for other things
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class BookingCache(models.Model):
    """
    A text cache of bookings. Rooms are text, and bookings for the same room and timeslot are combined into one.
    """
    year = models.IntegerField(default=0)  # no sense using a date here
    semester = models.CharField(max_length=10)  # "Fall", "Winter", or "Summer"
    weekday = models.CharField(max_length=10)  # "Monday", "Tuesday", etc
    start_time = models.TimeField()
    end_time = models.TimeField()
    occasions = models.CharField(max_length=10000)  # typically a course name and number, but leave it broad for other things
    room = models.CharField(max_length=1000)


class Tag(models.Model):
    """
    A tag for a room. For example, rooms in the Life Sciences Centre may also be tagged LSC for easier searchability
    """
    tag = models.CharField(max_length=1000)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)