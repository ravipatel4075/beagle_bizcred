from django.db import models
from django.contrib.auth.models import User
from bizcred import enums, validators
from bizcred import validators
from bizcred import methods
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module


class Pan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    pan_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[validators.pan_validator]
    )

    pan_card = models.FileField(
        upload_to=UploadPath('pan_card'),
        validators=[validators.file_validator],
    )

    def __str__(self):
        return self.user.username


class PanForm(base.BaseModelForm):
    class Meta:
        model = Pan
        exclude = ['user']


PAN_MODULE = Module(
    title="PAN Details",
    forms=[PanForm],
    model=Pan
)
