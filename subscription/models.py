from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from datetime import date
from markdownx.models import MarkdownxField

def first_day_of_current_month():
    today = date.today()
    return date(today.year, today.month, 1)

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('free', _('Free')),
        ('pro', _('Pro')),
        ('custom', _('Custom')),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    monthly_meal_limit = models.PositiveIntegerField(default=3)
    monthly_health_limit = models.PositiveIntegerField(default=1)
    unlimited_meals = models.BooleanField(default=False, verbose_name="Unlimited AI Meals")
    unlimited_health = models.BooleanField(default=False, verbose_name="Unlimited Health Reports")
    price_eur = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    description = MarkdownxField(blank=True, default="")

    def __str__(self):
        return self.get_name_display()


class AIUsage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_usages')
    month = models.DateField(default=first_day_of_current_month)
    meal_used = models.PositiveIntegerField(default=0)
    health_used = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"{self.user} - {self.month.strftime('%Y-%m')}"

    def is_reset_needed(self):
        return self.month < now().replace(day=1)

    def reset(self):
        self.month = now().replace(day=1)
        self.meal_used = 0
        self.health_used = 0
        self.save()