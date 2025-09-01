import uuid
from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL
# Create your models here.


# ----------------------
# Partner
# ----------------------


class Partner(models.Model):
    class PartnerType(models.TextChoices):
        NGO = "NGO", "NGO"
        GOV = "GOV", "Government"
        EMBASSY = "EMBASSY", "Embassy"
        CORPORATE = "CORPORATE", "Corporate"
        OTHER = "OTHER", "Other"

    class PartnerStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SUSPENDED = "suspended", "Suspended"
        BLACKLISTED = "blacklisted", "Blacklisted"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=PartnerType.choices)
    status = models.CharField(
        max_length=50, choices=PartnerStatus.choices, default=PartnerStatus.PENDING
    )
    risk_level = models.CharField(
        max_length=50, choices=RiskLevel.choices, default=RiskLevel.LOW
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partners_created",
    )
    departments = models.ManyToManyField(
        "users.Department",
        through="partners.PartnerDepartment",
        related_name="partners",
        blank=True,
    )

    def __str__(self):
        return self.name


# ----------------------
# PartnerProfile (1:1)
# ----------------------


class PartnerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.OneToOneField(
        Partner, on_delete=models.CASCADE, related_name="profile"
    )
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(max_length=100, blank=True, null=True)
    ownership_structure = models.TextField(blank=True, null=True)
    bank_details = models.TextField(blank=True, null=True)
    organization_type = models.CharField(max_length=50, blank=True, null=True)
    legal_history = models.TextField(blank=True, null=True)
    social_background = models.TextField(blank=True, null=True)
    financial_stability = models.TextField(blank=True, null=True)
    reputation = models.TextField(blank=True, null=True)
    esg_policies = models.TextField(blank=True, null=True)
    documents = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.partner.name}"


# ----------------------
# PartnerDocuments
# ----------------------
class PartnerDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="documents"
    )
    file_type = models.CharField(max_length=50)
    file_url = models.TextField()
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="documents_uploaded"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)


class StatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="status_history"
    )
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="status_changes"
    )
    changed_at = models.DateTimeField(auto_now_add=True)


class RiskLevelHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="risk_history"
    )
    old_risk = models.CharField(max_length=50)
    new_risk = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="risk_changes"
    )
    changed_at = models.DateTimeField(auto_now_add=True)


class PartnerDepartment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    department = models.ForeignKey("users.Department", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("partner", "department")

    def __str__(self):
        return f"{self.partner.name} ↔ {self.department.name}"
