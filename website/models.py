from django.db import models

class DisinfectionRun(models.Model):
    room_number = models.IntegerField()
    room_setup = models.IntegerField()
    run_count = models.IntegerField()
    master_ip = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    disinfect_status = models.CharField(max_length=255, default='Pending')  # Add disinfection status field

    def __str__(self):
        return f"Run {self.run_count} for Room {self.room_number}, Setup {self.room_setup} ({self.master_ip})"

