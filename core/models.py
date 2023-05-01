from django.db import models
from datetime import datetime
from users.models import CustomUser


class Location(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    code = models.CharField(max_length=128, unique=True, editable=False)
    latitude = models.DecimalField(
        max_digits=8, decimal_places=4, blank=False, null=False)
    longitude = models.DecimalField(
        max_digits=8, decimal_places=4, blank=False, null=False)
    radius = models.IntegerField(default=100, blank=False, null=False)
    qr_code_url = models.TextField(max_length=1024, blank=False, null=False)


class Attendance(models.Model):
    location = models.ForeignKey(
        Location, related_name='attendance', on_delete=models.CASCADE)
    employee = models.ForeignKey(
        CustomUser, related_name='attendance2', on_delete=models.CASCADE)
    date = models.DateField(auto_now=True, null=False)
    clock_in_time = models.TimeField(auto_now=True, null=False)
    # forgetting to clock out is a thing
    clock_out_time = models.TimeField(auto_now=False, null=True)


class LeaveRequest(models.Model):
    employee = models.ForeignKey(
        CustomUser, related_name="leave_request", on_delete=models.CASCADE)
    days_off = models.IntegerField(null=False)
    starting_date = models.DateField(null=False)
    message = models.TextField(max_length=2048, blank=True, null=True)
