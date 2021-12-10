from django.db import models
from django.contrib.auth.models import User
from bizcred import enums

class FinanceOfferDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    sanction_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    lender_interest_rate = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Lender's rate of interest",
    )
    veloce_margin = models.DecimalField(
        max_digits=7,
        decimal_places=2
    )
    effective_interest_rate = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Effective rate of interest",
    )
    emi_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    overdue_interest_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Overdue rate of interest",
    )
    
    veloce_margin_payer = models.SmallIntegerField(
        choices=enums.to_choices(enums.VeloceMarginPayer)
    )
    def __str__(self):
        return self.user.username
