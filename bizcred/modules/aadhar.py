from django.db import models
from django.contrib.auth.models import User
from bizcred import enums, validators
from bizcred.helpers import UploadPath
from bizcred import validators
from bizcred import methods
from bizcred.forms import base
from bizcred.modules.base import Module


class Aadhar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    aadhar_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[validators.aadhar_validator]
    )

    aadhar_card = models.FileField(
        upload_to=UploadPath('aadhar_card'),
        validators=[validators.file_validator]
    )
    def __str__(self):
        return self.user.username


class AadharForm(base.BaseModelForm):
    class Meta:
        model = Aadhar
        exclude = ['user']


AADHAR_MODULE = Module(
    title="Aadhar Details",
    forms=[AadharForm],
    model=Aadhar
)
