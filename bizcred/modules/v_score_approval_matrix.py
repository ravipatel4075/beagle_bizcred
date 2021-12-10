from django.db import models
from bizcred.modules.veloce_score import VeloceScore

class VeloceScoreApprovalMatrix(models.Model):
    veloce_score = models.OneToOneField(VeloceScore, on_delete=models.CASCADE)
    dealer_finance_amount = models.IntegerField()
    borrower_finance_amount = models.IntegerField()
    tenure_months = models.CharField(
        max_length=2,
        verbose_name="Tenure(months)"
    )
    rate_of_interest = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Rate of Interest(%)"
    )
    processing_fees = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Processing Fees(%)"
    )

    def __str__(self):
        return self.dealer_finance_amount
