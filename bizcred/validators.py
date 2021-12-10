from django.core import validators
from django.core.exceptions import ValidationError
from upload_validator import FileTypeValidator
import re

pan_validator = validators.RegexValidator(
    regex='^[A-Z]{3}[PCHABGJLFT][A-Z][0-9]{4}[A-Z]$',
    message='Invalid PAN number.'
)


phone_validator = validators.RegexValidator(
    regex='^[0-9]{10}$',
    message='Invalid phone number.'
)

name_validator = validators.RegexValidator(
    regex='^[A-Za-z]',
    # regex='[A-Za-z]{2,25}\s[A-Za-z]{2,25}',
    message='Invalid characters in name.'
)


pin_validator = validators.RegexValidator(
    regex='^[0-9]{6}$'
)


aadhar_validator = validators.RegexValidator(
    regex='^[0-9]{12}$',
    message='Aadhaar No. should have exactly 12 digits.'
)


bin_validator = validators.RegexValidator(
    regex='^[0-9]{25}$',
    message='BAN should have exactly 25 digits.'
)


ifsc_validator = validators.RegexValidator(
    regex='^[a-zA-Z0-9]{11}$',
    message='IFSC should be an 11-digit alphanumeric code.'
)

cin_validator = validators.RegexValidator(
    regex='^[LU][0-9]{5}[A-Z]{2}[12][0-9]{3}[P][TL][C][0-9]{6}$',
    # regex = '^[0-9]{21}',
    message='Invalid CIN.'
)

din_validator = validators.RegexValidator(
    regex='^[0-9]{8}$',
    message='DIN should have exactly 8 digits.'
)

llpin_validator = validators.RegexValidator(
    regex='^[A-Z]{3}-[0-9]{4}$',
    message='Invalid LLPIN number.'
)

gst_validator = validators.RegexValidator(
    regex='^[0-9][1-9][A-Z]{3}[PCHABGJLFT][A-Z][0-9]{4}[A-Z][0-9][Z][a-zA-Z0-9]$',
    message='Invalid GST Number.'
)

udyam_validator = validators.RegexValidator(
    regex='^[A-Z]{5}[A-Z]{2}[0-9]{2}[0-9]{7}$',
    message='Invalid Udyam Registration No.'
)

passport_validator = validators.RegexValidator(
    regex='^(?!^0+$)[a-zA-Z0-9]{3,20}$',
    message='Invalid Passport No.'
)

driving_license_validator = validators.RegexValidator(
    regex='^[A-Z]{2}[0-9]{13}$',
    message='Invalid Driving License No.'
)

dependent_validator = validators.RegexValidator(
    regex='^[0-9]{1}$',
    message='Dependents should be positive numbers.'
)

amount_validator = validators.RegexValidator(
    regex='^[0-9]{7}$',
    message='Amount should be a 7-digit value.'
)

def file_validator(self):
    """ This function is an amalgamation of two validations,
        file size validation, file type validation, anf file extension validation"""

    import os
    ext = os.path.splitext(self.name)[1]
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.docx', '.doc', '.odt', '.csv', '.xls', '.ODS', '.xlsx']

    # Checks whether the file has a valid extension.
    print(ext.lower(), valid_extensions)
    if not ext.lower() in valid_extensions:
        raise ValidationError('Invalid file type. Valid file types include: pdf, jpeg, gif, png, doc, odt, docx, csv, ODS ,xls, xlsx.')

    file_size = self.size

    if file_size > 2621440:  # 2.5MB
        raise ValidationError("The maximum file size that can be uploaded is 2.5MB")
    else:
        return self


def password_validator(value):
    if not len(value) >= 8 or not len(value) <= 50:
        raise ValidationError(
            'Password should be between 8-50 characters long.'
        )
    if not re.search('[A-Z]', value) or not re.search('[a-z]', value) \
            or not re.search('[0-9]', value) or not re.search('[^A-Za-z0-9]', value):
        raise ValidationError(
            'Password should contain at least one numeric, uppercase, lowercase and special letter.'
        )
