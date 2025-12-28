from django.db import models
from django.contrib.auth.models import User


class Lead(models.Model):
    # ===============================
    # Core Identity (IMPORTANT)
    # ===============================

    lead_name = models.CharField(
        max_length=200,
        help_text="Display name for the lead (e.g. ACME Website Enquiry)"
    )

    email = models.EmailField(blank=True)

    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('won', 'Won'),
        ('lost', 'Lost'),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    # ===============================
    # Ownership & Lifecycle
    # ===============================

    lead_owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_leads"
    )

    converted_to_client = models.BooleanField(default=False)

    # ===============================
    # Person Details (OPTIONAL)
    # ===============================

    salutation = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    job_title = models.CharField(max_length=100, blank=True)

    # ===============================
    # Lead Classification
    # ===============================

    series = models.CharField(
        max_length=100,
        default="CRM-LEAD-.YYYY.-",
        blank=True
    )

    source = models.CharField(max_length=100, blank=True)
    lead_type = models.CharField(max_length=50, blank=True)
    request_type = models.CharField(max_length=50, blank=True)

    # ===============================
    # Contact Info
    # ===============================

    mobile_no = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    phone_ext = models.CharField(max_length=10, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    fax = models.CharField(max_length=50, blank=True)

    # ===============================
    # Organization
    # ===============================

    organization_name = models.CharField(max_length=200, blank=True)
    annual_revenue = models.CharField(max_length=100, blank=True)
    territory = models.CharField(max_length=100, blank=True)
    no_of_employees = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    market_segment = models.CharField(max_length=100, blank=True)

    # ===============================
    # Address
    # ===============================

    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='India', blank=True)

    # ===============================
    # Qualification
    # ===============================

    qualification_status = models.CharField(
        max_length=50,
        default='Unqualified',
        blank=True
    )
    qualified_by = models.CharField(max_length=100, blank=True)
    qualified_on = models.DateField(null=True, blank=True)

    # ===============================
    # Additional Info
    # ===============================

    campaign_name = models.CharField(max_length=100, blank=True)
    print_language = models.CharField(max_length=50, default='English', blank=True)

    disabled = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=False)
    blog_subscriber = models.BooleanField(default=False)

    # ===============================
    # Timestamps & Soft Delete
    # ===============================

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_leads"
    )

    # ===============================
    # Helpers
    # ===============================

    @property
    def person_name(self):
        """Optional helper if lead represents a person"""
        return " ".join(filter(None, [self.first_name, self.last_name]))

    def __str__(self):
        return self.lead_name
