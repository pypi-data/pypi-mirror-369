from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.utils.crypto import get_random_string
from django.utils import timezone


User = settings.AUTH_USER_MODEL

def generate_code(length=8):
    return get_random_string(length=length).lower()

class ReferralCode(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referral_code")
    code = models.CharField(max_length=32, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            tries = 0
            while tries < 5:
                candidate = generate_code(8)
                if not ReferralCode.objects.filter(code=candidate).exists():
                    self.code = candidate
                    break
                tries += 1
            if not self.code:
                raise IntegrityError("Unable to generate unique referral code")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.owner} - {self.code}"


class ReferralClick(models.Model):
    referral = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name="clicks")
    ip = models.CharField(max_length=45, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    cookie_id = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.referral}"


class ReferralAttribution(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_MANUAL = "manual_review"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_MANUAL, "Manual Review"),
    ]

    referral = models.ForeignKey(ReferralCode, on_delete=models.CASCADE, related_name="attributions")
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ref_attribution")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["referral", "referred_user"]),
        ]
        
        
    def __str__(self):
        return f"{self.referral} - {self.referred_user} ({self.status})"


class Reward(models.Model):
    attribution = models.ForeignKey(ReferralAttribution, on_delete=models.CASCADE, related_name="rewards")
    type = models.CharField(max_length=32, default="credit")  # e.g., credit, coupon
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    issued = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.attribution} - {self.type} ({self.amount})"
