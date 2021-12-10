from django.db import models
from django.contrib.auth.models import User
from bizcred import validators, enums
from bizcred.forms import base
from bizcred.helpers import UploadTo
from bizcred.modules.base import Module
from django.core.exceptions import ValidationError
from datetime import date


YEARS = range(date.today().year - 50, date.today().year + 1)


# class EmploymentType(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     finance_type = models.SmallIntegerField(
#         choices=enums.to_choices(enums.EmploymentType),
#         verbose_name="Type of Employment"
#     )
#     is_completed = models.BooleanField(default=False)
#
#
# class SelfEmployedInfo(models.Model):
#     finance_type = models.OneToOneField(EmploymentType, on_delete=models.CASCADE)
#     finance_year = models.SmallIntegerField(
#         choices=zip(YEARS, YEARS)
#     )
#     turnover_revenue = models.IntegerField(
#         verbose_name="Turnover / Revenue"
#     )
#     profit_befor_interest = models.IntegerField(
#         verbose_name="Profit before interest"
#     )
#     interest_expense = models.IntegerField()
#     depreciate = models.IntegerField()
#     tax = models.IntegerField()
#     profite_after_tax = models.IntegerField()
#     capital_reserves = models.IntegerField(
#         verbose_name="Capital and Reserves"
#     )
#     total_borrowing = models.IntegerField()
#     current_assets = models.IntegerField()
#     current_liablities = models.IntegerField()
#     balance_sheet = models.FileField(
#         upload_to=UploadTo('bs'),
#         validators=[validators.file_validator]
#     )
#     pnl_statement = models.FileField(
#         verbose_name='P&L Statement',
#         upload_to=UploadTo('pnl'),
#         validators=[validators.file_validator]
#     )
#
#
# class SalariedInfo(models.Model):
#     finance_type = models.OneToOneField(EmploymentType, on_delete=models.CASCADE)
#     employment_type = models.CharField(max_length=30)
#     employment_industry = models.SmallIntegerField(
#         choices=enums.to_choices(enums.EmploymentIndustry),
#         verbose_name="Employment industry"
#     )
#     company_name = models.CharField(max_length=30)
#     designation = models.CharField(max_length=30)
#     working_years_in_company = models.IntegerField(verbose_name="Working years in company")
#     work_experience = models.IntegerField(verbose_name=" Total Work experience")
#     appointment_letter = models.FileField(upload_to=UploadTo("appointment"), validators=[validators.file_validator])
#     salary_slip = models.FileField(upload_to=UploadTo("salary_slip"), validators=[validators.file_validator])
#
#
# class EmploymentTypeForm(base.BaseModelForm):
#     class Meta:
#         model = EmploymentType
#         exclude = ['user', 'is_completed']
#
#
#
# class SelfEmployedInfoForm(base.BaseModelForm):
#     class Meta:
#         model = SelfEmployedInfo
#         exclude = ['finance_type']
#
#
# class SalariedInfoForm(base.BaseModelForm):
#     class Meta:
#         model = SalariedInfo
#         exclude = ['finance_type']
#
#
# # FINANCE_DETAILS_MODULE = Module(
# #     title="Finance Details",
# #     forms=[EmploymentTypeForm, SelfEmployedInfoForm, SalariedInfoForm],
# #     model=Aadhar
# # )
#
#
# FINANCE_DETAILS_MODULE = Module(
#     title="Financial Details",
#     smalltitle="Financial Details",
#     forms=[EmploymentTypeForm, SelfEmployedInfoForm, SalariedInfoForm],
#     model=EmploymentType,
#     level=2
# )
