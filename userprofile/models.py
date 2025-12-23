import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Userprofile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def is_otp_valid(self):

        if not self.otp or not self.otp_created_at :

            return False
        
        expiry_time = self.otp_created_at + datetime.timedelta(minutes = 10)
        
        return timezone.now() <= expiry_time
        