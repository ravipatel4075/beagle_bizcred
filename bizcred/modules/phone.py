from django.db import models
from django import forms
from bizcred.forms import base
from bizcred.modules.base import Module, ListModule
from django.contrib.auth.models import User
from bizcred import enums, validators
from django.core.exceptions import ValidationError
from bizcred import methods
from django.contrib import messages


class Phone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, validators=[validators.phone_validator])
    otp = models.CharField(max_length=6, default='', blank=True)
    is_complete = models.BooleanField(default=False)
    expiry_date = models.DateTimeField()
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class PhoneForm1(base.BaseModelForm):

    class Meta:
        model = Phone
        exclude = ['user', 'otp', 'is_complete', 'expiry_date', 'reject_reason']

    # def save(self, **kwargs):
    #     out = super().save(**kwargs)
    #     try:
    #         sent_otp = methods.sending_sms_otp(out, self.user)
    #         if sent_otp['status']:
    #             return out
    #         else:
    #             raise ValidationError(sent_otp['msg'])
    #             # self.add_error('phone_number', sent_otp['msg'])
    #             return sent_otp['msg']
    #     except Exception as e:
    #         raise ValidationError(e)


class PhoneForm2(base.BaseModelForm):
    skip_render = True
    force_save = True
    otp = forms.CharField(max_length=6, label="One Time Password")

    class Meta:
        model = Phone
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        methods.phone_verification(self, cleaned_data)

    def save(self, **kwargs):
        out = super().save(**kwargs)
        out.is_complete = True
        return out


PHONE_MODULE = ListModule(
    min_items=1,
    max_items=1,
    title="Phone Verification",
    forms=[PhoneForm1, PhoneForm2],
    model=Phone,
    level=1
)
