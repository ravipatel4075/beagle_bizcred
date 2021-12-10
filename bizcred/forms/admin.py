from django import forms
from bizcred.forms import base
from bizcred.modules import metadata


class ApplicationRejectForm(base.BaseModelForm):

    class Meta:
        model = metadata.Metadata
        fields = ["reject_reason"]
