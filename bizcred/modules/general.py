from django.db import models
from bizcred.forms import base
from bizcred.modules.base import Module
from django.contrib.auth.models import User
from bizcred import enums
from datetime import date
from bizcred import validators
from django import forms
from .company_details import CompanyDetails


class General(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    father_husband_no = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    org_name = models.CharField(
        verbose_name="Organization Name",
        max_length=30,
        null=True,
        blank=True,
    )

    pos_in_company = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )

    birthdate = models.DateField()
    gender = models.IntegerField(
        choices=enums.to_choices(enums.Gender)
    )
    marital_status = models.SmallIntegerField(
        choices=enums.to_choices(enums.MaritalStatus)
    )

    dependents = models.CharField(
        max_length=2,
        validators=[validators.dependent_validator],
        null=True,
        blank=True
    )

    net_monthly_income = models.SmallIntegerField(
        choices=enums.to_choices(enums.MonthlyIncome)
    )
    education_level = models.SmallIntegerField(
        choices=enums.to_choices(enums.EducationLevel)
    )

    associated_professional_institute = models.CharField(null=True, blank=True,
                                                         max_length=50)  # , verbose_name="Associated Professional Institute"
    registration_number = models.CharField(null=True, blank=True, max_length=15,
                                           verbose_name="Registration / Membership No")
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.user.username


class GeneralForm(base.BaseModelForm):
    first_name = forms.CharField(widget=forms.TextInput(), label="First Name <small class=asterisk>*</small>")
    last_name = forms.CharField(widget=forms.TextInput(), label="Last Name <small class=asterisk>*</small>")

    half = ['org_name', 'pos_in_company', 'marital_status', 'dependents', 'birthdate', 'gender', 'first_name',
            'last_name', 'associated_professional_institute', 'registration_number']
    field_order = ['first_name', 'last_name', 'father_husband_no', 'org_name']

    org_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'title': 'Organization Name...!'}))
    father_husband_no = forms.CharField(required=False, label="Father/Husband Name",
                                        widget=forms.TextInput(attrs={'title': 'Father/Husband Name...!'}))
    pos_in_company = forms.CharField(required=False, label="Position In Organization",
                                     widget=forms.TextInput(attrs={'title': 'Position In Organization ...!'}))
    gender = forms.ChoiceField(choices=enums.to_choices(enums.Gender), required=True,
                               label="Gender <small class=asterisk>*</small>",
                               widget=forms.Select(attrs={'title': 'Select Gender Type...!'}))
    marital_status = forms.ChoiceField(choices=enums.to_choices(enums.MaritalStatus), required=True,
                                       label="Marital Status <small class=asterisk>*</small>",
                                       widget=forms.Select(attrs={'title': 'Select Marital Status...!'}))
    dependents = forms.CharField(required=False,
                                 label="No Of Dependents",
                                 widget=forms.TextInput(attrs={'title': 'No Of Dependents...!'}))
    net_monthly_income = forms.ChoiceField(choices=enums.to_choices(enums.MonthlyIncome), required=True,
                                           label="Monthly Income <small class=asterisk>*</small>",
                                           widget=forms.Select(attrs={'title': 'Select Net Monthly Income...!'}))
    education_level = forms.ChoiceField(choices=enums.to_choices(enums.EducationLevel), required=True,
                                        label="Education Level <small class=asterisk>*</small>",
                                        widget=forms.Select(attrs={'title': 'Select Education Level...!'}))
    associated_professional_institute = forms.CharField(required=False,
                                                        label="Associated Professional Institute",
                                                        widget=forms.TextInput(attrs={
                                                            'title': 'Associated Professional Institute Maximum 50 Character...!'}))
    registration_number = forms.CharField(required=False,
                                          widget=forms.TextInput(
                                              attrs={'title': 'Registration / Membership No Maximum 15 Character...!'}),
                                          label="Prof.Institute Reg. / Membership No.")
    birthdate = forms.DateField(label="Birthdate <small class=asterisk>*</small>",
                                widget=forms.Widget(attrs={'title': 'Select Gender Type...!'}),
                                help_text='Note : Date of birth should be 18 years old from Today...!')

    class Meta:
        model = General
        exclude = ['user', 'reject_reason']

    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.user is not None:
            try:
                org = CompanyDetails.objects.get(user=self.user)
            except:
                org = None
            self.fields['first_name'].widget.attrs = {'disabled': True}
            self.fields['first_name'].required = False
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].widget.attrs = {'disabled': True}
            self.fields['last_name'].initial = self.user.last_name
            self.fields['last_name'].required = False
            self.fields['org_name'].widget.attrs = {'disabled': False}
            if org is not None:
                self.fields['org_name'].widget.attrs = {'disabled': True}
                self.fields['org_name'].initial = org.org_name
            self.fields['org_name'].required = False

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('birthdate')
        today = date.today()
        try:
            if (dob.year + 18, dob.month, dob.day) > (today.year, today.month, today.day):
                self.add_error("birthdate", "Age should not be less than 18.")
        except Exception as e:
            print(e)

    def save(self, **kwargs):
        out = super().save(**kwargs)
        if self.user is not None:
            try:
                org = CompanyDetails.objects.get(user=self.user)
            except:
                org = None
            if org is not None:
                out.org_name = org.org_name
        return out


GENERAL_MODULE = Module(
    title="General Information",
    forms=[GeneralForm],
    model=General
)
