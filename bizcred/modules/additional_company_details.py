from django.db import models
from django import forms
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module


class AdditionalCompanyDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[validators.pan_validator]
    )

    pan_card = models.FileField(
        upload_to=UploadPath('pan_card'),
        validators=[validators.file_validator],
        verbose_name="Pan Card  <small class=asterisk>*</small>"
    )

    gst_number = models.CharField(
        max_length=15,
        validators=[validators.gst_validator],
        null=True,
        blank=True,
    )

    gst_proof = models.FileField(
        upload_to=UploadPath('gst'),
        validators=[validators.file_validator],
        verbose_name="GSTIN No",
        null=True,
        blank=True,
    )

    udyog_aadhar_number = models.CharField(
        max_length=16,
        validators=[validators.udyam_validator],
        unique=True,
        verbose_name="Udyam Registration No.  <small class=asterisk>*</small>"
    )

    udyog_aadhar_card = models.FileField(
        upload_to=UploadPath('udyog_aadhar'),
        validators=[validators.file_validator],
        verbose_name="Udyam Registration Certificate  <small class=asterisk>*</small>"
    )

    shop_license = models.FileField(
        upload_to=UploadPath('shop_license'),
        validators=[validators.file_validator],
        null=True,
        blank=True,
    )

    rent_agreement = models.FileField(
        upload_to=UploadPath('rent_agreement'),
        verbose_name="Rent agreement or ownership document <small class=asterisk>*</small>",
        validators=[validators.file_validator],
    )

    constitution_docs = models.FileField(
        upload_to=UploadPath('constitution_doc'),
        verbose_name="Constitution Docs [MOA/AOA/Partnership Deed/LLP Agreement/Trust Deed/Bye Laws etc.] <small class=asterisk>*</small> ",
        validators=[validators.file_validator],
    )

    authorization_resolution = models.FileField(
        upload_to=UploadPath('resolution'),
        validators=[validators.file_validator],
        verbose_name="Authorization Resolution <small class=asterisk>*</small>",
    )

    shareholder_list = models.FileField(
        upload_to=UploadPath('shareholder'),
        validators=[validators.file_validator],
        verbose_name="List of shareholders/members",
        null=True,
        blank=True
    )
    reject_reason = models.TextField(default='', blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class AdditionalCompanyDetailsForm(base.BaseModelForm):
    half = ['auth_first_name', 'auth_middle_name', 'auth_last_name', 'auth_gender', 'auth_mobile_Num', 'auth_email_ID']

    pan_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'title': 'PAN No Detail...!'}),
                                 label="PAN <small class=asterisk>*</small>")
    gst_number = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'title': 'GST No should be 15 Digits...!'}),
                                 label="Gstin No")
    udyog_aadhar_number = forms.CharField(required=True,
                                          widget=forms.TextInput(attrs={'title': 'Udyam Registration No...!'}),
                                          label="Udyam Registration No <small class=asterisk>*</small>"
                                          )

    class Meta:
        model = AdditionalCompanyDetails
        exclude = ['user', 'reject_reason']


ADDITIONAL_COMPANY_DETAILS_MODULE = Module(
    title="Organization Additional Detail",  # "Additional Company Details",
    forms=[AdditionalCompanyDetailsForm],
    model=AdditionalCompanyDetails,
    level=2
)


class AuthAdditionalCompanyDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[validators.pan_validator]
    )

    pan_card = models.FileField(
        upload_to=UploadPath('pan_card'),
        validators=[validators.file_validator],
        verbose_name="Pan Card <small class=asterisk>*</small>",
    )
    aadhar_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[validators.aadhar_validator]
    )

    aadhar_card = models.FileField(
        upload_to=UploadPath('aadhar_card'),
        validators=[validators.file_validator],
        verbose_name="Aadhaar Card <small class=asterisk>*</small>",
    )
    din_number = models.CharField(max_length=12)  # , unique=True

    reject_reason = models.TextField(default='', blank=True, null=True)


class AuthAdditionalCompanyDetailsForm(base.BaseModelForm):
    half = ['auth_first_name', 'auth_middle_name', 'auth_last_name', 'auth_gender', 'auth_mobile_Num', 'auth_email_ID']

    pan_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'title': 'PAN No Detail...!'}),
                                 label="PAN <small class=asterisk>*</small>")
    aadhar_number = forms.CharField(required=True, widget=forms.TextInput(attrs={'title': 'Aadhaar No Detail...!'}),
                                    label="Aadhaar <small class=asterisk>*</small>")
    din_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'title': 'DIN No Detail...!'}),
                                 label="DIN")

    class Meta:
        model = AuthAdditionalCompanyDetails
        exclude = ['user', 'reject_reason']


Auth_ADDITIONAL_COMPANY_DETAILS_MODULE = Module(
    title="Auth Person Additional Detail",  # "Additional Company Details",
    forms=[AuthAdditionalCompanyDetailsForm],
    model=AuthAdditionalCompanyDetails,
    level=2
)
