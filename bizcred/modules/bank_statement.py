from django.db import models
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module, ListModule
from datetime import date
from bizcred import enums
from django import forms  # added by Piyush For Tool Tips of all fields.

YEARS = range(date.today().year - 1, date.today().year + 1)


class BankStatement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    year = models.SmallIntegerField(
        choices=zip(YEARS, YEARS)
    )
    month = models.TextField(max_length=255)

    statement = models.FileField(
        upload_to=UploadPath('bank_statement'),
        verbose_name="Bank Statement <small class=asterisk>*</small>",
        validators=[validators.file_validator]
    )
    is_complete = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)
    def __str__(self):
        return self.user.username


class BankStatementForm(base.BaseModelForm):
    half = ['year', 'month']

    year = forms.ChoiceField(choices=zip(YEARS, YEARS), required=True,
                             label="Year <small class=asterisk>*</small>",
                             widget=forms.Select(attrs={'title': 'Select Year...!'}))
    month = forms.MultipleChoiceField(label="Month <small class=asterisk>*</small>", choices=enums.to_choices(enums.Month), widget=forms.SelectMultiple(attrs={'title': 'Select Month...!'}))

    class Meta:
        model = BankStatement
        exclude = ['user', 'is_complete', 'reject_reason']

    def clean(self):
        cleaned = super().clean()
        year = cleaned.get('year')
        month = cleaned.get('month')
        if month:
            check_if_exists = BankStatement.objects.filter(user=self.user, year=year)
            if len(check_if_exists) > 0:
                error_mon_list = []
                for m_val in check_if_exists:
                    if any(check in month for check in m_val.month):
                        mon = int(m_val.month[2])
                        error_month = enums.Month(mon).name
                        error_mon_list.append(error_month.capitalize())
                if len(error_mon_list) > 0:
                    self.add_error("month", "Bank statement for {0} month(s) already exist.".format(', '.join(error_mon_list)))


BANKSTATEMENT_MODULE = ListModule(
    min_items=1,
    max_items=12,
    instance_title="Bank Statement",
    title="Bank Statements for last 12 Months",
    smalltitle="Bank Statements",
    forms=[BankStatementForm],
    model=BankStatement,
    level=3
)
