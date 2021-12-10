from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from bizcred import modules as mods
import random
from django.conf import settings
from django.core.exceptions import ValidationError
import requests
import json
import datetime
import pytz
from django.utils.crypto import get_random_string
from bizcred.modules.company_details import CompanyDetails
import base64
import xmltodict
import logging
from bizcred import enums
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMessage
import xml.etree.cElementTree as ET

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

OTP_LENGTH = 6
ORDERID_LENGTH = 8


def generate_otp():
    otp = [str(random.randint(0, 9)) for _ in range(OTP_LENGTH)]
    return ''.join(otp)


def generate_orderid():
    otp = [str(random.randint(1, 9)) for _ in range(ORDERID_LENGTH)]
    return ''.join(otp)


def register(form):
    password = User.objects.make_random_password()
    email = form.cleaned_data.get('email')
    first_name = form.cleaned_data.get('first_name')
    last_name = form.cleaned_data.get('last_name')

    user = User.objects.create_user(
        username=email,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    account_type = int(form.cleaned_data.get('account_type'))
    institution_name = form.cleaned_data.get('org_name')
    mods.metadata.Metadata(
        user=user,
        account_type=account_type,
        org_name=institution_name
    ).save()
    try:
        user_type = ''
        mail_subject = ''
        mail_subject1 = ''
        if account_type == 1:
            user_type = 'INDIVIDUAL'
            # mail_subject = ' Initial registration successful on Veloce'
            mail_subject = ' Initial registration successful on Beagle Bazaar'
            mail_subject1 = 'Initial registration of ' + first_name + ' ' + last_name + ' done on Beagle Bazaar'
        elif account_type == 2:
            user_type = 'INSTITUTION'
            mail_subject = ' Initial registration successful on Beagle Bazaar'
            # mail_subject = ' Initial registration successful on Veloce'
            mail_subject1 = 'Initial registration of ' + first_name + ' ' + last_name + ' done on Beagle Bazaar'
        else:
            user_type = "LENDER"
            # mail_subject = 'Initial Registration Done on Veloce'
            mail_subject = 'Initial Registration Done on Beagle Bazaar'
            mail_subject1 = 'A Lender’s Initial Registration Done on Beagle Bazaar'

        # email for user

        data = {
            'user': email,
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type,
            'password': password,
            'org_name': institution_name
        }
        message = get_template('mail/user-initial-registration.html').render(data)
        msg = EmailMessage(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
        )

        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

        # email for admin
        ctx = {
            'user': email,
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type,
            'org_name': institution_name
        }
        message = get_template('mail/user-registration-details.html').render(ctx)
        msg = EmailMessage(
            mail_subject1,
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        print("msg", msg)
    except Exception as e:
        print("mail sended")
        print(e)


def login(form, request):
    user = auth.authenticate(
        username=form.data['email'],
        password=form.data['password']
    )
    if user is not None:
        auth.login(request, user)
        return True
    else:
        return False


def save_profile(form, instance_dict, user):
    if form.force_save or instance_dict != form.instance.__dict__:
        profile_step = form.save(commit=False)
        try:
            company_details = CompanyDetails.objects.get(user=user)
            profile_step.company_details = company_details
        except Exception as e:
            pass
        try:
            profile_step.is_auto_gen = False
        except:
            pass
        profile_step.user = user
        profile_step.save()
        return True
    return False


def update_flags(meta, module, instance, index, updated, step, substep):
    if index < 0:
        if (not meta.is_complete(step) or updated) and module.steps == substep:
            meta.complete(step)
        elif index < 0 and updated and module.steps > substep:
            meta.incomplete(step)
    else:
        if instance and (not instance.is_complete or updated) and module.steps == substep:
            instance.is_complete = True
            instance.save()
        elif instance and module.steps > substep:
            instance.is_complete = False
            instance.save()

        completed = len(module.instances(meta.user).filter(is_complete=True))
        if completed >= module.min_items and (not meta.is_complete(step) or updated):
            meta.complete(step)
        elif completed < module.min_items:
            meta.incomplete(step)


def sending_sms_otp(request, user):
    # user_data = User.objects.get(id=user.id)
    current_date = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    otp = generate_otp()
    # out.expiry_date = current_date
    # out.otp = generate_otp()
    # out.is_verified = False
    try:
        url = settings.SMS_API_URL
        data = {
            'From': 'VCFINT',
            'To': request.POST['phone_number'],
            'TemplateName': 'OTP Template',
            'VAR1': user.first_name + ' ' + user.last_name,
            'VAR2': otp
        }
        response = requests.post(url, data=data).text
        status = json.loads(response)
        if status['Status'] == 'Success':
            out = mods.phone.Phone.objects.create(
                user=user,
                phone_number=request.POST['phone_number'],
                expiry_date=current_date,
                otp=otp,
            )
            out.save()
            context = {
                'status': True,
                'out': out,
                'otp': out.otp
            }
            return context
        else:
            context = {
                'status': False,
                'out': '',
                'msg': status['Details']
            }
            return context
    except:
        context = {
            'status': False,
        }
        return context


def phone_verification(self, cleaned_data):
    currenttime = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    current_date = self.instance.expiry_date
    expiry_date = current_date + datetime.timedelta(minutes=10)
    if expiry_date >= currenttime:
        if cleaned_data.get('otp') != self.instance.otp:
            self.add_error('otp', "Incorrect OTP.")
            # raise ValidationError("Incorrect OTP.")
    else:
        raise ValidationError("OTP expired")


def forgotpassword(form, user_info, request):
    user = form.data['email']
    code = get_random_string(length=8)
    if user_info:
        user_obj = mods.metadata.Metadata.objects.get(user=user_info)
        user_obj.password_code = code
        user_obj.password = make_password(code)
        user_obj.save()
        send_mail(
            "Verification Code for reset password",
            f"Your verification code is {code}.",
            settings.EMAIL_HOST_USER,
            [user],
            fail_silently=False
        )
    else:
        error = "Invalid email!"


def save_self_employed_details(form, finance_type, request):
    obj = form.save(commit=False)
    obj.finance_type = finance_type
    obj.save()


def save_salaried_details(form, finance_type):
    finance_info = form.save(commit=False)
    finance_info.finance_type = finance_type
    finance_info.save()


# level_status
def level_status(request, modules, meta):
    # print('meta',meta)#email
    status = []
    for level in range(1, 4): # three times loop run
        count = 0
        verified_count = 0
        counter = 0
        for i in range(len(modules)):
            # print(meta.is_complete(i))
            # print(modules[i])
            if not meta.is_complete(i) and modules[i].level == level:
                count += 1
                # print('count',count)
                counter = level
                # print('common',counter,level)
            elif not meta.is_verified(i) and modules[i].level == level:
                verified_count += 1
        status.append({
            'level': level,
            'count': count,
            'counter': counter,
            'verified_count': verified_count
        })
    # print(status)
    return status


def setup_logger(user, content):
    """To setup as many loggers as you want"""

    import time, os, fnmatch, shutil
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H%M%S', t)
    username = user.split("@")
    BACKUP_NAME = str(settings.BASE_DIR) + "/bizcred/crif_log/" + (str(username[0]) + "-crif-log-" + str(timestamp))
    print('*************************************************************')
    print(BACKUP_NAME)
    print('*************************************************************')
    with open(BACKUP_NAME + ".log", 'w+') as log_file_obj:
        log_file_obj.write(str(content))


def crif_score(request, user):

    if user.is_crif_generated == False:
        orderId = generate_orderid()
        user_data = User.objects.get(id=user.user.id)
        general_data = mods.general.General.objects.get(user=user.user)
        phone = mods.phone.Phone.objects.get(user=user.user)
        identity = mods.identification.Identification.objects.get(user=user.user)
        address1 = mods.address.Address.objects.get(user=user.user)
        firstname = user_data.first_name
        lastname = user_data.last_name
        middlename = general_data.father_husband_no
        dob = general_data.birthdate.strftime("%d-%m-%Y")
        marital_status = general_data.marital_status
        phone = str(phone.phone_number)
        email = 'cs.ishadada@gmail.com' #user_data.email
        pan = identity.pan_number
        dl = identity.driving_license_no  # 'ZNPEKW71699719'
        passport = identity.passport_no
        address = str(address1.unit_number)
        village = address1.city  # address1.street_address
        city = address1.city  # 'COLABA'
        state = address1.state  # address1.state  # 'RJ'
        state = enums.IndiaStates(state).name
        pin = str(address1.pin_code)
        country = 'india'  # Fix now
        customer_id = settings.MERCHANT_ID
        product_code = 'BBC_CONSUMER_SCORE#85#2.0'
        consent = 'Y'
        tz = pytz.timezone('Asia/Calcutta')
        date = datetime.datetime.now(tz)
        current_date = date.strftime("%d-%m-%Y %H:%M:%S")
        accessCode = settings.USER_ID + '|' + settings.MERCHANT_ID + '|' + product_code + '|' + settings.PASSWORD + '|' + str(
            current_date)
        accessCode = base64.b64encode(accessCode.encode("utf-8"))

        # STAG-1

        data1 = firstname + '||' + lastname + '||' + str(dob) + '|||' + str(phone) + '|||' + str(
            email) + '||' + str(pan) + '|' + str(dl) + '||' + str(passport) + '|||||||' + str(
            middlename) + '|' + str(address) + '|' + str(village) + '|' + str(city) + '|' + str(state) + '|' + str(
            pin) + '|' + country + '|||||||' + str(customer_id) + '|' + str(product_code) + '|' + consent + '|'
        headers = {
            'orderId': orderId,
            'accessCode': accessCode.decode('utf-8'),
            'appID': settings.APP_ID,
            'merchantID': customer_id,
            'Content-Type': 'text/plain',
        }
        response1 = requests.post(settings.CRIF_STAG_API_1, data=data1, headers=headers).text
        api_response1 = json.loads(response1) # error while approving user details
        reportId = api_response1['reportId']
        redirectURL = 'https://cir.crifhighmark.com/Inquiry/B2B/secureService.action'  # api_response1['redirectURL']
        PaymentFlag = 'N'
        alterFlag = 'N'
        reportFlag = 'Y'
        UserAns = 'Null'  # ["Jun-2007", " Jan-2017", " Jun-2017", " Jun-2005"]

        setup_logger(user.user.email, data1)
        setup_logger(user.user.email, response1)

        # STAG - 2
        data2 = orderId + '|' + reportId + '|' + str(accessCode.decode(
            'utf-8')) + '|' + redirectURL + '|' + PaymentFlag + '|' + alterFlag + '|' + reportFlag + '|' + UserAns
        headers2 = {
            'orderId': orderId,
            'accessCode': accessCode.decode('utf-8'),
            'appID': settings.APP_ID,
            'merchantID': customer_id,
            'Content-Type': 'text/plain',
            'reportId': reportId,
            'requestType': 'Authorization',
        }

        response2 = requests.post(settings.CRIF_STAG_API_2, data=data2, headers=headers2).text
        api_response2 = json.loads(response2)
        UserAns = 'Null'  # api_response2[optionList]  # ["Jun-2007", " Jan-2017", " Jun-2017", " Jun-2005"]
        if UserAns != 'Null' and api_response2['status'] == 'S11':
            for i in UserAns:
                data2 = orderId + '|' + reportId + '|' + str(accessCode.decode(
                    'utf-8')) + '|' + redirectURL + '|' + PaymentFlag + '|' + alterFlag + '|' + reportFlag + '|' + i
                headers = {
                    'orderId': orderId,
                    'accessCode': accessCode.decode('utf-8'),
                    'appID': settings.APP_ID,
                    'merchantID': customer_id,
                    'Content-Type': 'text/plain',
                    'reportId': reportId,
                    'requestType': 'Authorization',
                }
                response2 = requests.post(settings.CRIF_STAG_API_2, data=data2, headers=headers).text
                api_response2 = json.loads(response2)
                if api_response2['status'] == 'S01':
                    break
                else:
                    setup_logger(user.user.email, api_response2)
        else:
            setup_logger(user.user.email, response2)

        setup_logger(user.user.email, data2)
        setup_logger(user.user.email, headers2)
        setup_logger(user.user.email, response2)

        # STAG 3

        data3 = orderId + '|' + reportId + '|' + str(
            accessCode.decode('utf-8')) + '|' + redirectURL + '|' + PaymentFlag + '|' + alterFlag + '|' + reportFlag
        headers3 = {
            'orderId': orderId,
            'accessCode': accessCode.decode('utf-8'),
            'appID': settings.APP_ID,
            'merchantID': customer_id,
            'Content-Type': 'text/plain',
            'reportId': reportId,
        }
        response3 = requests.post(settings.CRIF_STAG_API_3, data=data3, headers=headers3)

        setup_logger(user.user.email, data3)
        setup_logger(user.user.email, headers3)
        setup_logger(user.user.email, response3)

        if response3.status_code == 200:
            user.is_crif_generated = True
            user.save()
            data_dict = xmltodict.parse(response3.text)
            json_data = json.dumps(data_dict)
            parsedData = json.loads(json_data)
            report = mods.crif_data.B2CReport.objects.create(
                user=user_data,
                orderid=orderId,
                data=parsedData
            )
            report.save()
            obj = mods.crif_data.B2CReport.objects.get(user=user_data)
            crif_score = 0
            if obj.data['B2C-REPORT']['SCORES']:
                crif_score = obj.data['B2C-REPORT']['SCORES']['SCORE']['SCORE-VALUE']
            try:
                mods.veloce_score_master.VeloceScoreMaster.objects.create(
                    user=user_data,
                    crif_score=crif_score
                )
            except Exception as e:
                mods.veloce_score_master.VeloceScoreMaster.objects.create(
                    user=user_data,
                    crif_score=0.0,
                    de_ratio=0,
                    current_ratio=0,
                    ebitda_percentage=0,
                    int_cov_ratio=0,
                    credit_rating=0,
                    credit_manage_score=0,
                    total_score=0
                )


def level_completion_email(form, level, meta, request):
    user = request.user
    user_info = User.objects.get(username=request.user)
    acc_type = enums.AccountType(meta.account_type).name

    if user_info:
        mods.level_email.LevelEmail(
            user=user_info,
            level=level
        ).save()

        if acc_type == 'LENDER':
            if level == 2:
                data = {
                    'user': user_info.email,
                    'first_name': user_info.first_name,
                    'last_name': user_info.last_name,
                    'user_type': acc_type,
                    'org_name': meta.org_name,
                    'level': level
                }
                message = get_template('mail/level-completion-user.html').render(data)
                mail_subject = 'Profile Information is successfully submitted'
                msg = EmailMessage(
                    mail_subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user_info.email],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                # email for admin
                ctx = {
                    'user': user_info.email,
                    'first_name': user_info.first_name,
                    'last_name': user_info.last_name,
                    'user_type': acc_type,
                    'org_name': meta.org_name,
                    'level': level
                }
                message = get_template('mail/level-completion-admin.html').render(ctx)
                mail_subject = 'Lender’s Profile Information Submitted'
                msg = EmailMessage(
                    mail_subject,
                    # level) + ' registration information submitted successfully',
                    message,
                    settings.EMAIL_HOST_USER,
                    settings.ADMIN_EMAILS,
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
        else:
            data = {
                'user': user_info.email,
                'first_name': user_info.first_name,
                'last_name': user_info.last_name,
                'user_type': acc_type,
                'org_name': meta.org_name,
                'level': level
            }
            message = get_template('mail/level-completion-user.html').render(data)
            mail_subject = 'Level – ' + str(level) + ' information successfully submitted on Beagle'

            msg = EmailMessage(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user_info.email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

            # email for admin
            ctx = {
                'user': user_info.email,
                'first_name': user_info.first_name,
                'last_name': user_info.last_name,
                'user_type': acc_type,
                'org_name': meta.org_name,
                'level': level
            }
            message = get_template('mail/level-completion-admin.html').render(ctx)
            mail_subject = 'Level – ' + str(
                level) + ' registration information submitted successfully by ' + user_info.first_name + ' ' + user_info.last_name
            # level) + ' registration information submitted successfully',

            msg = EmailMessage(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                settings.ADMIN_EMAILS,
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()


def level_approved_email(user, level, account_type, email_info, request):
    admin_user = request.user
    user_info = User.objects.get(username=user)
    acc_type = enums.AccountType(account_type).name
    meta = mods.metadata.Metadata.objects.get(user=user_info)

    if acc_type == 'LENDER':
        if level == 2:
            # email for user
            if user_info:
                email_info.is_approved = True
                email_info.save()
                data = {
                        'first_name': user_info.first_name,
                        'last_name': user_info.last_name,
                        'user_type': acc_type,
                        'org_name': meta.org_name,
                        'level': level
                        }
                message = get_template('mail/level-approved-user.html').render(data)
                mail_subject = 'Profile Approved at Beagle'

                msg = EmailMessage(
                    mail_subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [user_info.email],
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()

                # email for admin
                ctx = {
                    'user': user_info.email,
                    'first_name': user_info.first_name,
                    'last_name': user_info.last_name,
                    'user_type': acc_type,
                    'org_name': meta.org_name,
                    'approver': admin_user,
                    'level': level
                }
                message = get_template('mail/level-approved-admin.html').render(ctx)
                mail_subject = 'Lender Profile Approved'

                msg = EmailMessage(
                    mail_subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    settings.ADMIN_EMAILS,
                )
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
    else:
        if user_info:
            email_info.is_approved = True
            email_info.save()
            data = {
                'first_name': user_info.first_name,
                'last_name': user_info.last_name,
                'level': level
            }
            message = get_template('mail/level-approved-user.html').render(data)
            mail_subject = 'Level – ' + str(level) + ' registration information approved'

            msg = EmailMessage(
                mail_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user_info.email],
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()

        # email for admin
        ctx = {
            'user': user_info.email,
            'first_name': user_info.first_name,
            'last_name': user_info.last_name,
            'user_type': acc_type,
            'org_name': meta.org_name,
            'approver': admin_user,
            'level': level
        }
        message = get_template('mail/level-approved-admin.html').render(ctx)
        mail_subject = 'Level – ' + str(
            level) + ' registration information submitted successfully by ' + user_info.first_name + ' ' + user_info.last_name

        msg = EmailMessage(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()


def updated_info_approved_email(title, meta, request):
    user = request.user
    user_info = User.objects.get(username=request.user)
    acc_type = enums.AccountType(meta.account_type).name
    print("********************************", user_info)
    if acc_type == 'LENDER':
        ctx = {
            'user': user_info.email,
            'first_name': user_info.first_name,
            'last_name': user_info.last_name,
            'user_type': acc_type,
            'org_name': meta.org_name,
            'title': title
        }
        message = get_template('mail/form-updation-admin.html').render(ctx)
        mail_subject = str(title) + ' information updated successfully by ' + user_info.first_name + ' ' + user_info.last_name
        msg = EmailMessage(
            mail_subject,
            # level) + ' registration information submitted successfully',
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    else:

        ctx = {
            'user': user_info.email,
            'first_name': user_info.first_name,
            'last_name': user_info.last_name,
            'user_type': acc_type,
            'org_name': meta.org_name,
            'title': title
        }
        message = get_template('mail/form-updation-admin.html').render(ctx)
        mail_subject = str(title) + ' form updated successfully by ' + user_info.first_name + ' ' + user_info.last_name
        # level) + ' registration information submitted successfully',

        msg = EmailMessage(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()


def rejected_info_email(user, meta, title, module):
    # user = request.user
    # user_info = User.objects.get(username=request.user)
    acc_type = enums.AccountType(meta.account_type).name
    step_model = module.model.objects.get(user=user)
    reject_reason = step_model.reject_reason
    print("********************************", reject_reason, step_model)
    if acc_type == 'LENDER':
        ctx = {
            'user': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': acc_type,
            'org_name': meta.org_name,
            'title': title,
            'reject_reason': reject_reason
        }
        message = get_template('mail/form-rejection-user-email.html').render(ctx)
        mail_subject = 'Rejection of certain inappropriate registration information on Beagle'
        msg = EmailMessage(
            mail_subject,
            # level) + ' registration information submitted successfully',
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
    else:

        ctx = {
            'user': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': acc_type,
            'org_name': meta.org_name,
            'title': title,
            'reject_reason': reject_reason
        }
        message = get_template('mail/form-rejection-user-email.html').render(ctx)
        mail_subject = 'Rejection of certain inappropriate registration information on Beagle'

        msg = EmailMessage(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            settings.ADMIN_EMAILS,
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()


def array_dt(data_val):
    main_data_list = []
    bal_data = data_val.split('|')
    for cur_bal in bal_data:
        data_list = []
        if len(cur_bal) > 1:
            final_bal = cur_bal.split(",")
            disp_data = final_bal[-1]
            mon_y = final_bal[0].split(':')
            data_list.append(mon_y[0])
            data_list.append(mon_y[1])
            data_list.append(disp_data)
            main_data_list.append(data_list)
    return main_data_list


def convert_dl_to_html(data):
    html = ''
    for d_item in data:
        if d_item[0] == 'Jan':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Feb':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Mar':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Apr':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'May':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Jun':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Jul':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Aug':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Sep':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Oct':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Nov':
            html += '<td>' + d_item[1] + '</td>'
        elif d_item[0] == 'Dec':
            html += '<td>' + d_item[1] + '</td>'
        else:
            html += '<td>-</td>'
    return html

def month_list(month):
    html = ''
    for m_item in month:
        html += '<th>' + m_item + '</td>'
    return html
