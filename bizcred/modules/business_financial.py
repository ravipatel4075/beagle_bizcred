from django.db import models
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module, ListModule
from datetime import date
from django.core.validators import MinValueValidator
from django import forms  # added by Piyush For Tool Tips of all fields.

YEARS_RANGE = range(date.today().year - 4, date.today().year)
YEARS = []

for i in reversed(YEARS_RANGE):
    YEARS.append(str(i) + '-' + str(i + 1))


class BusinessFinancial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    finance_year = models.CharField(max_length=10)
    turnover_revenue = models.IntegerField(validators=[MinValueValidator(1)])
    profit_befor_interest = models.IntegerField(validators=[MinValueValidator(1)])
    interest_expense = models.IntegerField(validators=[MinValueValidator(1)])
    depreciate = models.IntegerField(validators=[MinValueValidator(1)])
    tax = models.IntegerField(validators=[MinValueValidator(1)])
    profite_after_tax = models.IntegerField(validators=[MinValueValidator(1)])
    capital_reserves = models.IntegerField()
    total_borrowing = models.IntegerField()
    current_assets = models.IntegerField()
    current_liablities = models.IntegerField()

    balance_sheet = models.FileField(
        verbose_name='Balance Sheet Report <small class=asterisk>*</small>',
        upload_to=UploadPath('bs'),
        validators=[validators.file_validator]
    )

    pnl_statement = models.FileField(
        verbose_name='P&L Statement <small class=asterisk>*</small>',
        upload_to=UploadPath('pnl'),
        validators=[validators.file_validator]
    )

    certified_audit_report = models.FileField(
        verbose_name='Certified Audit Report',
        upload_to=UploadPath('car'),
        null=True,
        blank=True,
        validators=[validators.file_validator]
    )

    is_complete = models.BooleanField(default=False)
    is_auto_gen = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class BusinessFinancialForm(base.BaseModelForm):
    half = ['finance_year', 'turnover_revenue', 'profit_befor_interest', 'interest_expense',
            'depreciate', 'tax', 'profite_after_tax', 'capital_reserves', 'total_borrowing',
            'current_assets', 'current_liablities']

    finance_year = forms.ChoiceField(choices=zip(YEARS, YEARS), required=True,
                                     label="Financial Year <small class=asterisk>*</small>",
                                     widget=forms.Select(attrs={'title': 'Select Financial Year...!'}))
    # turnover_revenue = forms.CharField(required=True, label="Turnover / Revenue  <small class=asterisk>*</small>",
    #                                    widget=forms.TextInput(attrs={'title': 'Turnover / Revenue Detail ...!'}))
    # profit_befor_interest = forms.CharField(required=True,
    #                                         label="Profit before interest Depreciation & Taxes  <small class=asterisk>*</small>",
    #                                         widget=forms.TextInput(attrs={
    #                                             'title': 'Profit before interest Depreciation & Taxes  Detail ...!'}))
    # interest_expense = forms.CharField(required=True, label="Interest <small class=asterisk>*</small>",
    #                                    widget=forms.TextInput(attrs={'title': 'Interest...!'}))
    # depreciate = forms.CharField(required=True, label="Depreciation  <small class=asterisk>*</small>",
    #                              widget=forms.TextInput(attrs={'title': 'Depreciate Detail...!'}))
    # tax = forms.CharField(required=True, label="Tax  <small class=asterisk>*</small>",
    #                       widget=forms.TextInput(attrs={'title': 'Tax Detail...!'}))
    # profite_after_tax = forms.CharField(required=True, label="Profit After Taxes <small class=asterisk>*</small>",
    #                                     widget=forms.TextInput(attrs={'title': 'Profit After Taxes Detail...!'}))
    # capital_reserves = forms.CharField(required=True, label="Capital and Reserves <small class=asterisk>*</small>",
    #                                    widget=forms.TextInput(attrs={'title': 'Capital and Reserves Detail...!'}))
    # total_borrowing = forms.CharField(required=True, label="Total Borrowing <small class=asterisk>*</small>",
    #                                   widget=forms.TextInput(attrs={'title': 'Total borrowing Detail...!'}))
    # current_assets = forms.CharField(required=True, label="Current Assets <small class=asterisk>*</small>",
    #                                  widget=forms.TextInput(attrs={'title': 'Current Assets Detail...!'}))
    # current_liablities = forms.CharField(required=True, label="Current Liablities <small class=asterisk>*</small>",
    #                                      widget=forms.TextInput(attrs={'title': 'Current Liablities Detail...!'}))

    class Meta:
        model = BusinessFinancial  # CompanyDetails
        exclude = ['user', 'is_complete', 'is_auto_gen', 'reject_reason']

    def clean(self):
        cleaned = super().clean()
        finance_year = cleaned.get('finance_year')
        if len(BusinessFinancial.objects.filter(user=self.user, finance_year=finance_year)) > 0:
            self.add_error("finance_year", "Business Financial for this finance year already exists.")


BUSINESS_FINANCIAL_MODULE = ListModule(
    min_items=3,
    max_items=3,
    instance_title="Year",
    title="Business Financials",  # "Company Details",
    forms=[BusinessFinancialForm],
    model=BusinessFinancial,
    level=3
)
