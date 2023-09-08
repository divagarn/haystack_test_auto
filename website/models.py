from django.db import models

class DisinfectionRun(models.Model):
    room_number = models.IntegerField()
    room_setup = models.IntegerField()
    run_count = models.IntegerField()
    master_ip = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    robot_name = models.CharField(max_length=100, default='NONE')

    def __str__(self):
        return f"Run {self.run_count} for Room {self.room_number}, Setup {self.room_setup} ({self.master_ip})"

class FilteredData(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    hour = models.IntegerField()
    min = models.IntegerField()
    room = models.IntegerField()
    percentage = models.IntegerField()
    duration = models.IntegerField()
    image = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(default='0.0.0.0')

    class Meta:
        db_table = 'robot_data_append_table'

# class RunningStatus(models.Model):
#     running_status = models.CharField(max_length=100, default='')

#     class Meta:
#         db_table = ''