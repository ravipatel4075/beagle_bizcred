from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module
from django.core.exceptions import ValidationError
from bizcred import validators
from django.conf import settings
from django import forms  # added by Piyush For Tool Tips of all fields.


class Identification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    din = models.CharField(
        verbose_name="DIN (if director anywhere)",
        null=True,
        blank=True,
        max_length=8,  # before 20 Piyush
        validators=[validators.din_validator]
    )

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[validators.pan_validator]
    )

    pan_card = models.FileField(
        upload_to=UploadPath('pan_card'),
        verbose_name="PAN Card <small class=asterisk>*</small>",
        validators=[validators.file_validator],
    )

    aadhar_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[validators.aadhar_validator]
    )

    aadhar_card = models.FileField(
        upload_to=UploadPath('aadhar_card'),
        verbose_name="Aadhaar Card <small class=asterisk>*</small>",
        validators=[validators.file_validator]
    )

    gst_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[validators.gst_validator]
    )

    gst_proof = models.FileField(
        upload_to=UploadPath('gst'),
        null=True,
        blank=True,
        validators=[validators.file_validator]
    )

    passport_no = models.CharField(
        max_length=8,  # before 20 Piyush
        null=True,
        blank=True,
        validators=[validators.passport_validator]
    )

    passport_expiry_date = models.DateField(null=True, blank=True)

    passport = models.FileField(
        upload_to=UploadPath('paasport'),
        verbose_name="Passport",
        null=True,
        blank=True,
        validators=[validators.file_validator],
        help_text=(
            'Note : Please provide information for minimum any 1 out of Passport OR Driving License OR Voter id OR Utility Bill.')
    )

    driving_license_no = models.CharField(
        max_length=15,  # before 20 Piyush
        null=True,
        blank=True,
        validators=[validators.driving_license_validator]
    )

    driving_license_expiry_date = models.DateField(
        blank=True,
        null=True
    )

    driving_license = models.FileField(
        upload_to=UploadPath('driving_license'),
        verbose_name="Driving Licence",
        null=True,
        blank=True,
        validators=[validators.file_validator],
        help_text=(
            'Note : Please provide information for minimum any 1 out of Passport OR Driving License OR Voter id OR Utility Bill.')
    )

    voter_id = models.FileField(
        upload_to=UploadPath('voter_id'),
        verbose_name="Voter ID",
        null=True,
        blank=True,
        validators=[validators.file_validator],
        help_text=(
            'Note : Please provide information for minimum any 1 out of Passport OR Driving License OR Voter id OR Utility Bill.')
    )

    utility_bill = models.FileField(
        upload_to=UploadPath('utility_bill'),
        verbose_name="Utility Bill",
        null=True,
        blank=True,
        validators=[validators.file_validator],
        help_text=(
            'Note : Please provide information for minimum any 1 out of Passport OR Driving License OR Voter id OR Utility Bill.')
    )
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class IdentificationForm(base.BaseModelForm):
    half = ['passport_no', 'passport_expiry_date', 'driving_license_no', 'driving_license_expiry_date']

    din = forms.CharField(required=False, label="DIN (if director anywhere)",
                          widget=forms.TextInput(attrs={'title': 'DIN Number Detail ...!'}))
    pan_number = forms.CharField(required=True,
                                 label="Pan Number <small class=asterisk>*</small> [ Permanent Account Number ]",
                                 widget=forms.TextInput(attrs={'title': 'Pan Number Detail ...!', 'style': 'text-transform:uppercase;'}))
    aadhar_number = forms.CharField(required=True, label="Aadhar Number <small class=asterisk>*</small>",
                                    widget=forms.TextInput(attrs={'title': 'Aadhar Number Detail ...!'}))
    gst_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'title': 'GSTIN Number Detail ...!', 'style': 'text-transform:uppercase;'}))
    passport_no = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'title': 'Passport Number Detail ...!', 'style': 'text-transform:uppercase;'})
                                  )
    driving_license_no = forms.CharField(required=False,
                                         widget=forms.TextInput(attrs={'title': 'Driving License Number Detail ...!', 'style': 'text-transform:uppercase;'}))

    class Meta:
        model = Identification
        exclude = ['user', 'reject_reason']

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('voter_id') and not cleaned_data.get('driving_license') and not cleaned_data.get(
                'passport') and not cleaned_data.get('utility_bill'):
            raise ValidationError(
                "At least one of the following should be provided: Voter ID/Passport/Driving License/Utility Bill.")


IDENTIFICATION_MODULE = Module(
    title="Identification Documents",
    smalltitle="Identification",
    forms=[IdentificationForm],
    model=Identification,
    level=2
)
