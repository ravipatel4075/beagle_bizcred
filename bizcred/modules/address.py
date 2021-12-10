from django.db import models
from bizcred.forms import base
from bizcred.modules.base import Module
from django.contrib.auth.models import User
from bizcred import validators
from bizcred import enums
from bizcred.helpers import UploadPath
from datetime import date
from django import forms  # added by Piyush For Tool Tips of all fields.
from .metadata import Metadata

YEARS = range(date.today().year - 50, date.today().year + 1)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    unit_number = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    tel_number = models.CharField(
        max_length=11,
        null=True,
        blank=True
    )
    pin_code = models.CharField(
        max_length=6,
        validators=[validators.pin_validator]
    )

    city = models.CharField(
        max_length=40
    )
    state = models.SmallIntegerField(
        choices=enums.to_choices(enums.IndiaStates)
    )

    effective_year = models.SmallIntegerField(
        choices=zip(YEARS, YEARS),
        verbose_name="Effective Since Year"
    )
    effective_month = models.SmallIntegerField(
        choices=enums.to_choices(enums.Month),
        verbose_name="Effective Month"
    )

    proof = models.FileField(
        upload_to=UploadPath('address_proof'),
        validators=[validators.file_validator],
        verbose_name="Address Proof <small class=asterisk>*</small>")

    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class AddressForm(base.BaseModelForm):
    half = ['tel_number', 'pin_code', 'effective_year', 'effective_month', 'state', 'city']

    unit_number = forms.CharField(required=True,
                                  label="Floor/Unit <small class=asterisk>*</small>",
                                  widget=forms.TextInput(attrs={'title': 'Floor/Unit Detail...!'}))
    street_address = forms.CharField(required=True,
                                     label="Street Address <small class=asterisk>*</small>",
                                     widget=forms.TextInput(attrs={'title': 'Street Address Detail...!'}))
    tel_number = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={'title': 'Telephone number...!'}),
                                 label="Telephone No.",
                                 help_text='Note : If Multiple telephone no then add comma separated ...!')
    pin_code = forms.CharField(required=True,
                               label="Pin Code <small class=asterisk>*</small>",
                               widget=forms.TextInput(attrs={'title': 'Pin Code Detail...!'}))
    city = forms.CharField(required=True,
                           label="City <small class=asterisk>*</small>",
                           widget=forms.TextInput(attrs={'title': 'City Detail...!'}))
    state = forms.ChoiceField(choices=enums.to_choices(enums.IndiaStates), required=True,
                              label="State <small class=asterisk>*</small>",
                              widget=forms.Select(attrs={'title': 'State Detail...!'}))
    effective_year = forms.ChoiceField(choices=zip(YEARS, YEARS), required=True,
                                       label="Effective Year <small class=asterisk>*</small>",
                                       widget=forms.Select(attrs={'title': 'Effective Year Detail...!'}))
    effective_month = forms.ChoiceField(choices=enums.to_choices(enums.Month), required=True,
                                        label="Effective Month <small class=asterisk>*</small>",
                                        widget=forms.Select(attrs={'title': 'Effective Month Detail...!'}))
    proof = forms.FileField(required=True, label="Address Proof <small class=asterisk>*</small>", error_messages={'required': 'Select a file'})

    class Meta:
        model = Address
        exclude = ['user', 'reject_reason']

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(AddressForm, self).__init__(*args, **kwargs)
        # get_user_type = Metadata.objects.get(use)
        try:
            if self.user.metadata.account_type == 1:
                self.fields['tel_number'].required = False
            else:
                self.fields['tel_number'].required = True
        except:
            pass


CURRENT_ADDRESS_MODULE = Module(
    title="Current Address",
    forms=[AddressForm],
    model=Address,
    level=1
)

OFFICE_ADDRESS_MODULE = Module(
    title="Office Address",
    forms=[AddressForm],
    model=Address,
    level=1
)
