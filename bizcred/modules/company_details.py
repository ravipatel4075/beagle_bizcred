from django.db import models
from django.contrib.auth.models import User
from bizcred.forms import base
from bizcred.modules.base import Module
from django.core.exceptions import ValidationError
from bizcred import enums, validators
from datetime import date
from bizcred.modules import metadata
from django import forms

YEARS = range(date.today().year - 50, date.today().year + 1)


class CompanyDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    org_name = models.CharField(
        max_length=30,
    )

    org_website = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Organization Website",
    )

    org_type = models.SmallIntegerField(
        choices=enums.to_choices(enums.OrganizationType),
    )

    company_register_no = models.CharField(
        max_length=21,
        null=True,
        blank=True,
        verbose_name="CIN/LLPIN <small class=asterisk>*</small>",
        validators=[validators.cin_validator],
    )

    soc = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="SOC <small class=asterisk>*</small>"
    )

    year = models.SmallIntegerField(
        choices=zip(YEARS, YEARS),
    )
    month = models.SmallIntegerField(
        choices=enums.to_choices(enums.Month),
    )
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.org_name


class CompanyDetailsForm(base.BaseModelForm):
    half = ['org_name', 'org_website', 'org_type', 'company_register_no', 'soc', 'pos_in_company', 'year', 'month']

    org_name = forms.CharField(widget=forms.TextInput(attrs={'title': 'Organization Name Detail...!'}),
                               required=False, label="Organization Name <small class=asterisk>*</small>")
    org_website = forms.CharField(widget=forms.TextInput(attrs={'title': 'Organization Website Detail...!'}),
                                  required=False,
                                  label="Organization Website")
    org_type = forms.ChoiceField(choices=enums.to_choices(enums.OrganizationType),
                                 widget=forms.Select(attrs={'title': 'Select Organization Type...!'}),
                                 label="Organization Type <small class=asterisk>*</small>")
    year = forms.ChoiceField(choices=zip(YEARS, YEARS),
                             required=True,
                             label="Establishment Year <small class=asterisk>*</small>",
                             widget=forms.Select(attrs={'title': 'Establishment Year Detail...!'}))
    month = forms.ChoiceField(choices=enums.to_choices(enums.Month),
                              required=True,
                              label="Establishment Month <small class=asterisk>*</small>",
                              widget=forms.Select(attrs={'title': 'Establishment Month Detail...!'}))

    class Meta:
        model = CompanyDetails
        exclude = ['user', 'reject_reason']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('org_type') == enums.OrganizationType.LLP:
            if not cleaned_data.get('company_register_no'):
                raise ValidationError("At least one of the following should be provided: CIN/LLPIN")
            else:
                raise ValidationError("Please provide: Soc Reg Number.")
        if cleaned_data.get('org_type') == '1' or cleaned_data.get('org_type') == '2' or cleaned_data.get(
                'org_type') == '3':
            if not cleaned_data.get('company_register_no') or cleaned_data.get(
                    'company_register_no') == '' or cleaned_data.get('company_register_no') == ' ' or cleaned_data.get(
                    'company_register_no') is None:
                company_register_no = forms.CharField(widget=forms.TextInput(attrs={'title': 'CIN/LLPIN No...!'}),
                                                      required=True,
                                                      label="CIN/LLPIN <small class=asterisk>*</small>")
                # soc = None  # self.cleaned_data.get('soc')
                raise ValidationError("At least one of the following should be provided: CIN/LLPIN")

        if cleaned_data.get('org_type') == '4' or cleaned_data.get('org_type') == '5' or cleaned_data.get(
                'org_type') == '6':
            if not cleaned_data.get('soc') or cleaned_data.get('soc') == '' or cleaned_data.get(
                    'soc') == ' ' or cleaned_data.get('soc') is None:
                soc = forms.CharField(widget=forms.TextInput(attrs={'title': 'Reg No Detail...!'}),
                                      required=True,
                                      label="Reg No. <small class=asterisk>*</small>")
                raise ValidationError("Please provide: SOC")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user is not None:
            org = metadata.Metadata.objects.get(user=self.user)
            self.fields['org_name'].initial = org.org_name


COMPANY_DETAILS_MODULE = Module(
    title="Organization Details",  # "Company Details",
    forms=[CompanyDetailsForm],
    model=CompanyDetails
)
