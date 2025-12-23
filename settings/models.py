from django.db import models


class AppSetting(models.Model):
    app_name = models.CharField(max_length=100, default="Teal CRM")

    # IMPORTANT: default="" prevents NULL migration issues
    base_url = models.URLField(blank=True, default="")

    logo = models.ImageField(
        upload_to="branding/",
        blank=True,
        null=True
    )

    # SMTP SETTINGS
    smtp_host = models.CharField(max_length=255, blank=True)
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_username = models.CharField(max_length=255, blank=True)
    smtp_password = models.CharField(max_length=255, blank=True)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_use_ssl = models.BooleanField(default=False)
    smtp_from_email = models.EmailField(blank=True)

    def __str__(self):
        return "Application Settings"
