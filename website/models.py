from django.db import models

class DisinfectionRun(models.Model):
    room_number = models.IntegerField()
    room_setup = models.IntegerField()
    run_count = models.IntegerField()
    master_ip = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Run {self.run_count} for Room {self.room_number}, Setup {self.room_setup} ({self.master_ip})"

class PrefilledData(models.Model):
    ID = models.IntegerField(primary_key=True)
    YEAR = models.IntegerField()
    MONTH = models.IntegerField()
    DAY = models.IntegerField()
    HOUR = models.IntegerField()
    MIN = models.IntegerField()
    ROOM = models.IntegerField()
    PERCENTAGE = models.IntegerField()
    DURATION = models.IntegerField()
    IMAGE = models.TextField()
    DATE = models.TextField()
    STATUS = models.TextField()

    class Meta:
        db_table = 'HAYSTACK_DISINFECT_REPORT'