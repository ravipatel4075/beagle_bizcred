from django.db import models
from django.contrib.auth.models import User
from bizcred import validators
from bizcred.forms import base
from bizcred.helpers import UploadPath
from bizcred.modules.base import Module, ListModule
from django.core.exceptions import ValidationError
from bizcred import enums
from django import forms  # added by Piyush For Tool Tips of all fields.


class EmploymentDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    employment_industry = models.SmallIntegerField(
        choices=enums.to_choices(enums.EmploymentIndustry),
    )
    company_name = models.CharField(max_length=30, null=True, blank=True)
    designation = models.CharField(max_length=30, null=True, blank=True)
    working_years_in_company = models.DecimalField(max_digits=4,
                                                   decimal_places=1, null=True, blank=True)
    work_experience = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    appointment_letter = models.FileField(verbose_name="Appointment Letter <small class=asterisk>*</small>", upload_to=UploadPath("appointment"), validators=[validators.file_validator], null=True, blank=True)
    salary_slip = models.FileField(verbose_name='Salary Slip [Last 6 Month] <small class=asterisk>*</small>',
                                   upload_to=UploadPath("salary_slip"),
                                   validators=[validators.file_validator], null=True, blank=True)
    is_auto_gen = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.company_name


class EmplymentDetailForm(base.BaseModelForm):
    half = ['company_name', 'designation', 'working_years_in_company', 'work_experience']

    employment_industry = forms.ChoiceField(choices=enums.to_choices(enums.EmploymentIndustry), required=True,
                                            label="Employment industry <small class=asterisk>*</small>",
                                            widget=forms.Select(attrs={'title': 'Select Employment industry...!'}))
    company_name = forms.CharField(required=True, label="Company Name  <small class=asterisk>*</small>",
                                   widget=forms.TextInput(attrs={'title': 'Company Name Detail ...!'}))
    designation = forms.CharField(required=True, label="Designation  <small class=asterisk>*</small>",
                                  widget=forms.TextInput(attrs={'title': 'Designation Detail ...!'}))
    working_years_in_company = forms.CharField(required=True,
                                               label="Working Years in Company <small class=asterisk>*</small>",
                                               widget=forms.TextInput(
                                                   attrs={'title': 'Working Years in Company Detail ...!'}))
    work_experience = forms.CharField(required=True, label="Work Experience  <small class=asterisk>*</small>",
                                      widget=forms.TextInput(attrs={'title': 'Work Experience Detail ...!'}))

    class Meta:
        model = EmploymentDetail
        exclude = ['user', 'is_auto_gen', 'reject_reason']


EMPLOYMENT_DETAIL_MODULE = Module(
    title="Employment Detail",
    forms=[EmplymentDetailForm],
    model=EmploymentDetail,
    level=3
)
