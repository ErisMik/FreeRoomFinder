from django.db import models

# Create your models here.


class Room:
    """
    A single room on a campus
    """
    campus = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    number = models.CharField(max_length=100) # some room numbers have letters in them
    capacity = models.IntegerField(default=0) # can guess this from max class sizes


class RoomBookedSlot:
    """
    A single booking for a room
    """
    year = models.IntegerField(default=0) # no sense using a date here
    semester = models.CharField(max_length=10) # "Fall", "Winter", or "Summer"
    weekday = models.CharField(max_length=10) # "Monday", "Tuesday", etc
    start_time = models.TimeField()
    end_time = models.TimeField()
    occasion = models.CharField() # typically a course name and number, but leave it open for other things