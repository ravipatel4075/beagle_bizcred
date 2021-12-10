from django.db import models
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module, ListModule
from datetime import date
from django import forms  # added by Piyush For Tool Tips of all fields.

YEARS_RANGE = range(date.today().year - 4, date.today().year)
YEARS = []

for i in reversed(YEARS_RANGE):
    YEARS.append(str(i) + '-' + str(i + 1))


class IncomeTaxReturn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    year = models.CharField(
        choices=zip(YEARS, YEARS),
        max_length=10
    )

    tax_return = models.FileField(
        upload_to=UploadPath('itr'),
        verbose_name="Tax Return <small class=asterisk>*</small>",
        validators=[validators.file_validator],
    )

    is_complete = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class IncomeTaxReturnForm(base.BaseModelForm):
    year = forms.ChoiceField(choices=zip(YEARS, YEARS), required=True,
                             label="Financial Year <small class=asterisk>*</small>",
                             widget=forms.Select(attrs={'title': 'Select Financial Year...!'}))

    class Meta:
        model = IncomeTaxReturn
        exclude = ['user', 'is_complete', 'reject_reason']

    def clean(self):
        cleaned = super().clean()
        year = cleaned.get('year')
        if len(IncomeTaxReturn.objects.filter(user=self.user, year=year)) > 0:
            self.add_error("year", "An income tax return for this year already exists.")


ITR_MODULE = ListModule(
    min_items=3,
    max_items=3,
    instance_title="ITR - Year",
    title="Income Tax Return for last 3 years",
    smalltitle="Income Tax Returns",
    forms=[IncomeTaxReturnForm],
    model=IncomeTaxReturn,
    level=3
)
