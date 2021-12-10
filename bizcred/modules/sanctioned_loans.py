from django.core.validators import MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import ListModule
from bizcred import validators
from datetime import date
from django import forms


class SanctionedLoan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    sanction_date = models.DateField(
        null=True,
        blank=True
    )
    loan_amount = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)
    loan_tenure = models.PositiveIntegerField(default=0, blank=True, null=True)
    loan_emi = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    letter = models.FileField(
        upload_to=UploadPath('loan_sanction_letter'),
        validators=[validators.file_validator],
        null=True,
        blank=True,
        verbose_name='Sanction Letter'
    )

    lender_noc = models.FileField(
        upload_to=UploadPath('lender_noc'),
        validators=[validators.file_validator],
        null=True,
        blank=True,
        verbose_name='Lender Bank NOC, If Loan is Fully Paid up',
    )

    is_complete = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class SanctionedLoanForm(base.BaseModelForm):
    half = ['sanction_date', 'loan_amount', 'loan_tenure', 'loan_emi']

    # loan_amount = forms.CharField(required=False, empty_value=0, label="Loan Amount",
    #                               widget=forms.TextInput(attrs={'title': 'Loan Amount Detail...!'}))
    loan_tenure = forms.CharField(required=False, empty_value=0, label="Loan Tenure (Months)",
                                  widget=forms.TextInput(attrs={'title': 'Loan Tenure (Months) Detail...!'}))

    class Meta:
        model = SanctionedLoan
        exclude = ['user', 'is_complete', 'reject_reason']

    def clean(self):
        cleaned_data = super().clean()
        sanction_date = cleaned_data.get('sanction_date')
        loan_amount = cleaned_data.get('loan_amount')
        loan_emi = cleaned_data.get('loan_emi')
        today = date.today()
        try:
            if (sanction_date.year, sanction_date.month, sanction_date.day) > (today.year, today.month, today.day):
                self.add_error("sanction_date", "Sanction Date should not be a future date.")
            if loan_emi > loan_amount:
                self.add_error("loan_emi", "Loan EMI should not be greater than Loan amount.")
        except Exception as e:
            pass


SANCTIONED_LOANS_MODULE = ListModule(
    min_items=0,
    max_items=10,
    instance_title="Letter",
    title="Previous Loans Details",
    smalltitle="Previous Loans Details",
    forms=[SanctionedLoanForm],
    model=SanctionedLoan,
    level=3
)
