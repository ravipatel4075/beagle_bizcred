from django.db import models
from django import forms
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module


class GstRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gst_number = models.CharField(
        max_length=15,
        unique=True,
    )

    gst_proof = models.FileField(
        upload_to=UploadPath('gst'),
        validators=[validators.file_validator]
    )
    def __str__(self):
        return self.user.username


class GstForm(base.BaseModelForm):
    gst_number = forms.CharField(widget=forms.TextInput(attrs={'title': 'GST No should be 15 Digits...!'}))

    class Meta:
        model = GstRegistration
        exclude = ['user']


GST_MODULE = Module(
    title="GST Details",
    forms=[GstForm],
    model=GstRegistration
)

OPTIONAL_GST_MODULE = Module(
    title="GST Details",
    forms=[GstForm],
    model=GstRegistration,
    level=3
)
