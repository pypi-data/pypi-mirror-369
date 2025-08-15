from django.db import models
from django.conf import settings

from .mixin import BillingControllerMixin
from .manager import BillingAccountManager


class BillingAccount(models.Model, BillingControllerMixin):
    class AccountTypes(models.IntegerChoices):
        INDIVIDUAL = 1, "Individual"
        ORGANIZATION = 2, "Organization"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="billing_account",
        null=True,
        blank=True,
    )
    account_number = models.CharField(max_length=255, unique=True)
    account_type = models.IntegerField(
        choices=AccountTypes.choices, default=AccountTypes.INDIVIDUAL
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    objects = BillingAccountManager()

    def __str__(self):
        return f"{self.user} - {self.account_number}"
