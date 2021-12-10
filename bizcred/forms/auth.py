from django import forms
from bizcred.forms.base import *
from django.core import validators
from bizcred.validators import *
from django.core.exceptions import ValidationError
from bizcred import enums
import re
from django.contrib.auth.models import User

TERMS_CONDITIONS_LABEL = """
    I have read, understood, and I agree to the <a href="http://innovations.veloce.market/terms-of-use" target="_blank">Terms and Conditions</a>
    set forth by Beagle Bazaar and I agree to the same.
"""

PRIVACY_POLICY_LABEL = """
    I agree to Beagle Bazaar requesting, processing and utilizing my personal data as
    mentioned in <a href="http://innovations.veloce.market/privacy-policy" target="_blank">Privacy Policy</a> of Beagle Bazaar.
"""


class RegisterForm(BaseForm):
    account_type = forms.ChoiceField(
        choices=enums.to_choices(enums.AccountType)
    )

    org_name = forms.CharField(
        max_length=50,
        min_length=1,
        label="Organization Name"
    )

    first_name = forms.CharField(
        max_length=50,
        min_length=1,
        validators=[name_validator]
    )

    last_name = forms.CharField(
        max_length=50,
        min_length=1,
        validators=[name_validator]
    )

    # if re.name_validator('[A-Za-z]{2,25}\s[A-Za-z]{2,25}', string):
    #     print("true")
    # else:
    #     print("false")

    email = forms.EmailField(
        max_length=60
        # validators=[validators.EmailValidator()]
    )

    terms_and_conditions = forms.BooleanField(
        widget=widgets.CustomCheckbox(label=TERMS_CONDITIONS_LABEL),
        label=""
    )

    privacy_policy = forms.BooleanField(
        widget=widgets.CustomCheckbox(label=PRIVACY_POLICY_LABEL),
        label=""
    )

    half = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['org_name'].required = False


class ChangePasswordForm(BaseForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(),
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[password_validator]
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[password_validator]
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            self.add_error('confirm_password', "Passwords don't match.")
            raise ValidationError("Passwords don't match.")


class LoginForm(BaseForm):
    email = forms.EmailField(
        max_length=60
        # validators=[validators.EmailValidator()]
    )

    password = forms.CharField(
        widget=forms.PasswordInput(),
    )


class ForgotPasswordForm(BaseForm):
    email = forms.EmailField(
        max_length=60
        # validators=[validators.EmailValidator()]
    )


class VerifyCodeForm(BaseForm):
    code = forms.CharField(
        max_length=10,
    )


class UpdatePasswordForm(BaseForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        validators=[password_validator]
    )
