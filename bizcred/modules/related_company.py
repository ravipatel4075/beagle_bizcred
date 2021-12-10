from django.db import models
from django.contrib.auth.models import User
from bizcred.forms import base
from bizcred.modules.base import Module, ListModule
from bizcred import validators
from bizcred.modules.company_details import CompanyDetails
from bizcred.modules import metadata



class RelatedCompanyInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_details = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE, null=True, blank=True)

    related_website = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Related Company website",
    )

    related_company = models.CharField(
        max_length=100,
        verbose_name="Related Company / Firm Name"
    )
    related_company_address = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Related companies address",
    )
    related_company_gstin = models.CharField(
        max_length=15,
        verbose_name="Related companies gstin (Optional)",
        null=True,
        blank=True,
        validators=[validators.gst_validator]
    )
    is_complete = models.BooleanField(default=False)
    reject_reason = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.related_company

    class Meta:
        unique_together = ('related_company', 'company_details')


class RelatedCompanyInfoForm(base.BaseModelForm):
    half = ['related_website', 'related_company', 'related_company_address', 'related_company_gstin']

    # website = models.CharField(required=False, label="Comapny website",
    #                               widget=models.TextField(attrs={'title': 'Comapny website Detail...!'}))
    # related_company = models.CharField(required=False, label="Related Company / Firm Name",
    #                               widget=models.TextField(attrs={'title': 'Related Company / Firm Name Detail...!'}))

    class Meta:
        model = RelatedCompanyInfo
        exclude = ['user', 'is_complete', 'company_details', 'related_company', 'reject_reason']

    field_order = ['related_company', 'website']

    def save(self, *args, **kwargs):
        company = super().save(**kwargs)
        print(company)
        if self.user is not None:
            org = metadata.Metadata.objects.get(user=self.user)
            org_obj = CompanyDetails.objects.get(org_name=org.org_name)
            print(self.user, "********************************************", org_obj)
            company.related_company = org.org_name
            company.company_details = org_obj
            print("++++++++++++++++++++++++++++++++++++++", company)
            return company


RELATED_COMPANY_MODULE = ListModule(
    min_items=0,
    max_items=10,
    instance_title="Group Company",
    title="Group Company Details",
    smalltitle="Group Company",
    forms=[RelatedCompanyInfoForm],
    model=RelatedCompanyInfo,
    level=3
)
