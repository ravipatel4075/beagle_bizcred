from django.db import models
from django import forms  # added by Piyush For Tool Tips of all fields.24/07/2020
from django.contrib.auth.models import User
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module
from bizcred import validators
import json
from bizcred import enums
from django import forms


def bank_name():
    with open("bizcred/static/json/banknames.json") as f:
        json_data = json.load(f)
        data = tuple(json_data.items())
        return data


BANKACCOUNTTYPE = (
    (1, "CURRENT"),
    (2, "SAVINGS"),
    (3, "CC/OD"),
)


class Bank(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    ifsc_code = models.CharField(
        validators=[validators.ifsc_validator],
        # verbose_name="IFSC Code <small class=asterisk>*</small>",
        max_length=11,
    )

    branch_name = models.CharField(
        max_length=100,  # Before 150 Piyush
    )

    bank_name = models.CharField(
        max_length=100
    )

    bank_address = models.CharField(
        max_length=200,
    )

    bank_acc_type = models.SmallIntegerField(
        # max_length=15,
        verbose_name="Account Type",
        default=1
    )

    account_no = models.CharField(
        max_length=20,  # Before 50 Piyush
        verbose_name="Bank Account No.",
    )

    branch_manager_name = models.CharField(
        max_length=50,
        verbose_name="Branch Manager Name",
    )

    branch_manager_email = models.EmailField(
        max_length=50,  # Before 60 Piyush
        verbose_name="Branch Manager Email",
    )

    branch_manager_phone_number = models.CharField(
        max_length=10,
        validators=[validators.phone_validator],
        verbose_name="Branch Manager Mobile"
    )

    cancel_cheque = models.FileField(
        upload_to=UploadPath('cancel_cheque'),
        verbose_name="Cancel Cheque <small class=asterisk>*</small>",
        validators=[validators.file_validator]
    )
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username

class BankForm(base.BaseModelForm):
    ifsc_code = forms.CharField(label="IFSC Code <small class=asterisk>*</small>",
                                widget=forms.TextInput(attrs={'title': 'IFSC Code Should be 11 Digits...!'}))
    branch_name = forms.CharField(label="Branch Name <small class=asterisk>*</small>",
                                  widget=forms.TextInput(attrs={'title': 'Branch Name...!'}))
    bank_name = forms.CharField(label="Bank Name <small class=asterisk>*</small>",
                                widget=forms.TextInput(attrs={'title': 'Bank Name...!'}))
    bank_address = forms.CharField(label="Bank Address <small class=asterisk>*</small>",
                                   widget=forms.TextInput(attrs={'title': 'Bank Address...!'}))
    bank_acc_type = forms.ChoiceField(label="Bank Account Type <small class=asterisk>*</small>",
                                      choices=BANKACCOUNTTYPE,
                                      widget=forms.Select(attrs={'title': 'Seelct Bank Account Type...!'}))
    account_no = forms.CharField(label="Bank Account No <small class=asterisk>*</small>",
                                 widget=forms.TextInput(attrs={'title': 'Bank Account No Detail...!'}))
    branch_manager_name = forms.CharField(required=False,
                                          widget=forms.TextInput(attrs={'title': 'Bank Manager Name...!'}))
    branch_manager_email = forms.CharField(required=False,
                                           widget=forms.TextInput(attrs={'title': 'Bank Manager EmailID...!'}))
    branch_manager_phone_number = forms.CharField(required=False,
                                                  widget=forms.TextInput(attrs={'title': 'Bank Manager Mobile No...!'}))

    half = ['ifsc_code', 'branch_name', 'bank_acc_type', 'account_no', 'branch_manager_email',
            'branch_manager_phone_number']

    class Meta:
        model = Bank
        exclude = ['user', 'reject_reason']


BANK_MODULE = Module(
    title="Bank Account Details",  # "Bank Documents",
    forms=[BankForm],
    model=Bank,
    level=2
)


class LenderDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    banking_license_no = models.CharField(
        max_length=20,
        verbose_name="Banking License No."
    )

    banking_license = models.FileField(
        upload_to=UploadPath('banking_license'),
        validators=[validators.file_validator],
        verbose_name='BANKING LICENSE <small class=asterisk>*</small>'
    )

    # No Objection Certificate-NOC
    noc = models.FileField(
        upload_to=UploadPath('noc'),
        validators=[validators.file_validator],
        verbose_name='RBI NOC <small class=asterisk>*</small>'
    )
    manager_remark = models.TextField(
        blank=True,
        null=True,
        verbose_name="Lender's Remark",
    )
    reject_reason = models.TextField(default='', blank=True, null=True)


class LenderDetailsForm(base.BaseModelForm):
    banking_license_no = forms.CharField(required=True,
                                         widget=forms.TextInput(attrs={'title': 'Banking License No Detail...!'}),
                                         label="Banking License No <small class=asterisk>*</small>")
    manager_remark = forms.CharField(required=False,
                                     widget=forms.Textarea(attrs={'title': 'Lenders Remark Detail...!',
                                                                  'rows': 5, 'cols': 40}),
                                     label="Lender's Remark")

    class Meta:
        model = LenderDetails
        exclude = ['user', 'reject_reason']
        widgets = {
            'manager_remark': forms.Textarea(attrs={'rows': 4, 'cols': 15})
        }


Lender_Details_MODULE = Module(
    title="Lender Details",  # "Lender Details Form",
    forms=[LenderDetailsForm],
    model=LenderDetails,
    level=2
)
