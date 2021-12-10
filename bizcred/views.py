from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse, HttpResponse
from django.shortcuts import render, redirect, HttpResponse, Http404, reverse, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from bizcred import forms, form_map, methods, enums, crif_commercial, models
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from bizcred import forms, form_map
from bizcred import methods
from bizcred.modules.base import ListModule
from django.core.files.storage import default_storage
from bizcred import modules as mods
from django.db.models import F
import re, json, time, requests, magic
import magic, datetime, pytz
from bizcred import enums, crif_commercial
from bizcred.render import render_to_pdf
import re
from django.contrib.auth.models import User
import requests
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import json, time
from django.core.exceptions import ValidationError
from django.conf import settings
import difflib
from django.core.serializers import serialize


def register(request):
    success = ''
    error = ''
    form = forms.auth.RegisterForm()
    if request.method == 'POST':
        form = forms.auth.RegisterForm(request.POST)
        email = request.POST['email']
        if form.is_valid():
            try:
                is_user_exit = User.objects.get(email=email)
            except:
                is_user_exit = ''
            if not is_user_exit:
                try:
                    methods.register(form)
                    return redirect('/accounts/login?success=1')
                except:
                    error = "User with this email already exists."
            else:
                error = "User with this email already exists."
    return render(request, 'register.html', {
        'form': form,
        'success': success,
        'error': error
    })


def login(request):
    error = ''
    success = ''
    if request.user:
        if request.user.is_authenticated:
            return redirect('overview')
    if request.GET.get('success', '') == '1':
        success = "Registration successful! Please check your email for a temporary password."
    form = forms.auth.LoginForm()
    if request.method == 'POST':
        form = forms.auth.LoginForm(request.POST)
        if form.is_valid():
            if methods.login(form, request):
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                    #return redirect('overview')
                return redirect("step", 1, 1)
            else:
                error = 'Incorrect login details.'
    return render(request, 'login.html', {'form': form, 'error': error, 'success': success})


def logout(request):
    auth.logout(request)
    if request.GET.get("next"):
        return redirect(request.GET.get("next"))
    return redirect('login')


@login_required
def change_password(request):
    error = ''
    success = ''
    user = auth.get_user(request)
    counter = 0
    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    mask = form_map.MASKS[meta.account_type]
    status = methods.level_status(request, modules, meta)
    for i in status:
        if i['counter'] > 0 and i['level'] > 1:
            counter = i['counter']
            break
        elif i['counter'] == 1:
            counter = 1
            break
    if request.method == 'POST':
        form = forms.auth.ChangePasswordForm(request.POST, label_suffix='')
        if form.is_valid():
            user = auth.authenticate(username=request.user.username, password=form.data['current_password'])
            if user:
                request.user.set_password(form.data['new_password'])
                request.user.save()
                success = 'Password changed successfully.'
                # auth.login(request, user)
                return redirect('login')
            else:
                form.add_error("current_password", "Current password is incorrect.")
    else:
        form = forms.auth.ChangePasswordForm(label_suffix='')

    return render(request, 'change-password.html', {
        'form': form,
        'error': error,
        'success': success,
        'level_status': status,
        'counter': counter,
        'step': 0,
        'modules': modules,
        'meta': meta,
        'complete': meta.equals_mask(mask),
    })


@login_required
def overview(request):
    user = auth.get_user(request)
    meta = user.metadata
    general = user.general
    counter = 0
    # print('############## meta',meta.account_type)# user account_type  = level wise = 1,2,3
    modules = form_map.FORM_MAP[meta.account_type]
    # print('############## models',len(modules))#10,12,8
    mask = form_map.MASKS[meta.account_type]
    # print('###############',mask) # masks 7,15,15
    status = methods.level_status(request, modules, meta)
    # print('full_status',status) # full_status [{'level': 1, 'count': 0, 'counter': 0, 'verified_count': 0}, {'level': 2, 'count': 2, 'counter': 2, 'verified_count': 0}, {'level': 3, 'count': 5, 'counter': 3, 'verified_count': 0}]
    for i in status:
        # print('status for',i)
        if i['counter'] > 0 and i['level'] > 1:
            counter = i['counter']
            break
        elif i['counter'] == 1:
            counter = 1
            break

    # print('after_status_change',status) # after_status_change [{'level': 1, 'count': 0, 'counter': 0, 'verified_count': 0}, {'level': 2, 'count': 2, 'counter': 2, 'verified_count': 0}, {'level': 3, 'count': 5, 'counter': 3, 'verified_count': 0}]
    return render(request, 'overview.html', {
        'modules': modules,
        'meta': meta,
        'complete': meta.equals_mask(mask),
        'level_status': status,
        'counter': counter
    })


@login_required
def admin_profiles(request):
    if not request.user.is_superuser:
        return redirect('/')

    users = []
    for account_type in form_map.FORM_MAP:
        mask = form_map.MASKS[account_type]
        users += mods.metadata.Metadata.objects.filter(
            account_type=account_type
        ).annotate(
            completed=F('completion').bitand(mask),
            reviewed=F('completion').bitand(F('profile_reviewed'))
        ).filter(
            completed=mask
        ).exclude(
            reviewed=F('completion')
        ).all()
    # methods.crif_score(request)  # comment from priya
    return render(request, 'admin/list-profiles.html', {
        'metas': users,
        'account_types': dict(enums.to_choices(enums.AccountType))
    })


@login_required
def admin_view(request, uid):
    if not request.user.is_superuser:
        return redirect('/')

    user = auth.models.User.objects.get(id=uid)
    meta = user.metadata
    mask = form_map.MASKS[meta.account_type]
    modules = form_map.FORM_MAP[meta.account_type]
    if request.method == 'POST':
        step = request.POST.get("step")
        status = methods.level_status(request, modules, meta)
        for i in status:
            if i['level'] == modules[int(step) - 2].level and (i['verified_count'] == 1 or i['verified_count'] == 0):
                try:
                    email_data = mods.level_email.LevelEmail.objects.get(user=user, level=modules[int(step) - 2].level,
                                                                         is_approved=False)
                except:
                    email_data = ''
                if email_data:
                    methods.level_approved_email(user, modules[int(step) - 2].level, meta.account_type, email_data,
                                                 request)
        if step and step.isnumeric():
            meta.approve(int(step) - 1)
            if int(step) == 8:
                meta.approve(int(step) - 1)
        print('***** CRIF_GEN ****', settings.CRIF_GEN)
        if settings.CRIF_GEN == True:
            if mods.metadata.Metadata.objects.filter(user_id=uid, profile_verified=1023):
                methods.crif_score(request, meta)
            crif_user = mods.metadata.Metadata.objects.filter(user_id=uid, profile_reviewed=4095)
            print('crif generate ******** ----------------->', crif_user)
            if crif_user:
                if not meta.is_crif_generated:
                    print('crif generate ----------------->', crif_user)
                    report_id, order_id, user_data = crif_commercial.crif_institution_stage_1(request, uid, meta)
                    time.sleep(10)
                    data = crif_commercial.crif_institution_stage_2(request, report_id, order_id, user_data)
                    time.sleep(10)
                    response = crif_commercial.crif_institution_stage_3(request,report_id, order_id, user_data)

    return render(request, 'admin/view-profile.html', {
        'modules': modules,
        'meta': meta,
        'complete': meta.equals_mask(mask),
        'target_user': user,
    })


@login_required
def admin_reject(request, uid, step):
    if not request.user.is_superuser:
        return redirect('/')
    print(step)
    user = auth.models.User.objects.get(id=uid)
    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    module = modules[int(step)]
    if request.method == 'POST':
        form = forms.admin.ApplicationRejectForm(request.POST, instance=meta)
        if form.is_valid():
            meta.reject(step, form.data.get("reject_reason"))
            module.model.objects.filter(user=user).update(reject_reason=request.POST["reject_reason"])
            methods.rejected_info_email(user, meta, module.title, module)
            return redirect("view-profile", uid)
    else:
        form = forms.admin.ApplicationRejectForm()

    return render(request, 'admin/reject-profile.html', {
        'meta': meta,
        'form': form
    })


@login_required
def profile_step(request, step, substep=1, index=-1):
    step -= 1
    flag = False
    next_step = False
    counter = 0
    user = auth.get_user(request)
    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    status = methods.level_status(request, modules, meta)
    if step < 0:
        return redirect('step', 1, 1)
    elif step >= len(modules):
        return redirect('overview')
    module = modules[step]
    if isinstance(module, ListModule) and index < 0:
        return redirect('list-step', step + 1)
    if isinstance(module, ListModule) and index > module.max_items:
        return redirect('list-step', step + 1)
    instance, instance_dict = module.instance(user, abs(index) - 1)
    form = module.get_form(substep)
    for i in status:
        if i['level'] == 1 and i['count'] == 0:
            if module.level == 2:
                counter = 0
                break
            else:
                counter = 1
        elif i['level'] == 2 and i['count'] == 0:
            if module.level == 3:
                counter = 0
                break
        # elif i['level'] == 3 and i['count'] == 0:
        #     if module.level == 4:
        #         counter = 0
        #         break
        elif module.level == 1:
            counter = 0
            break
        else:
            counter = 1
    if request.method == 'POST':
        sent_otp = ''
        if (step == 2 or step == 1) and not instance:
            sent_otp = methods.sending_sms_otp(request, user)
            try:
                if sent_otp['out']:
                    instance = sent_otp['out']
            except Exception as e:
                sent_otp = ''
        form_instance = form(request.POST, request.FILES, user=request.user, instance=instance, step=step)
        try:
            if form_instance.is_valid():
                if step == 6:
                    try:
                        business = mods.business_financial.BusinessFinancial.objects.filter(user=user)
                        if len(business) > 1:
                            employee_detail = mods.employment_details.EmploymentDetail(
                                user=request.user,
                                employment_industry=1,
                                company_name='test',
                                designation='test',
                                working_years_in_company=1,
                                work_experience=1,
                                appointment_letter='appointment00b5ffb0-13e9-4db2-893a-9f83087bbe6e.png',
                                salary_slip='appointment00b5ffb0-13e9-4db2-893a-9f83087bbe6e.png',
                                is_auto_gen=True
                            )
                            employee_detail.save()
                            meta.complete(step+1)
                    except:
                        pass
                elif step == 7:
                    employ_detail = mods.employment_details.EmploymentDetail.objects.filter(user=user)
                    if not employ_detail:
                        try:
                            business_detail = mods.business_financial.BusinessFinancial.objects.get(user=user)
                            business_detail.is_dummy = True
                            business_detail.save()
                        except:
                            business_detail = mods.business_financial.BusinessFinancial(
                                user=user,
                                finance_year=0,
                                turnover_revenue=0,
                                profit_befor_interest=0,
                                interest_expense=0,
                                depreciate=0,
                                tax=0,
                                profite_after_tax=0,
                                capital_reserves=0,
                                total_borrowing=0,
                                current_assets=0,
                                current_liablities=0,
                                balance_sheet='appointment00b5ffb0-13e9-4db2-893a-9f83087bbe6e.png',
                                pnl_statement='appointment00b5ffb0-13e9-4db2-893a-9f83087bbe6e.png',
                                certified_audit_report='appointment00b5ffb0-13e9-4db2-893a-9f83087bbe6e.png',
                                is_complete=True,
                                is_auto_gen=True
                            )
                            business_detail.save()
                            meta.complete(step-1)
                try:
                    if (sent_otp and sent_otp['out'] and (step == 2 or step == 1)) or not sent_otp:
                        print(instance_dict)
                        updated = methods.save_profile(form_instance, instance_dict, user)
                        print(updated, "**************updated*******************")
                        methods.update_flags(meta, module, form_instance.instance, index, updated, step, substep)
                        try:
                            email_data = mods.level_email.LevelEmail.objects.get(user=user, level=module.level, is_approved=True)
                        except:
                            email_data = ''
                        if updated and email_data:
                            methods.updated_info_approved_email(module.title, meta, request)
                        for l in status:
                            if l['level'] == module.level and l['count'] > 1:
                                flag = True
                                break
                            elif l['level'] == module.level and (l['count'] == 1 or l['count'] == 0):
                                try:
                                    email_data = mods.level_email.LevelEmail.objects.get(user=request.user, level=module.level)
                                except:
                                    email_data = ''
                                if not email_data:
                                    methods.level_completion_email(form_instance, module.level, meta, request)
                            else:
                                flag = False

                        if "phone_number" in request.POST:
                            messages.success(request,
                                             'OTP has been successfully sent on {0} Mobile number and OTP expire Within 10 mins.'.format(
                                                 request.POST['phone_number']))

                        next_stp = 1
                        for i in range(step, len(modules)):
                            next_step = meta.is_complete(i + 1)
                            if next_step:
                                next_stp = i + 1
                            else:
                                next_stp = i
                                break
                        if module.steps > substep:
                            return redirect('index-step', step + 1, substep + 1, index)
                        if index > 0:
                            return redirect('list-step', step + 1)
                        else:
                            if next_step:
                                return redirect('step', next_stp, 1)
                            else:
                                return redirect('step', next_stp + 2, 1)
                    else:
                        if 'number' in sent_otp['msg']:
                            messages.error(request, "Invalid phone number!")
                        else:
                            messages.error(request, "Something went wrong!")
                except Exception as e:
                    print("+++++++++++++++++++++++++++++++++------------", e)
        except forms.base.SkipStep:
            return redirect('step', step + 2, 1)
    else:
        form_instance = form(instance=instance, user=request.user, step=step)
    return render(request, 'step.html', {
        'form': form_instance,
        'step': step + 1,
        'num_steps': len(modules),
        'meta': meta,
        'modules': modules,
        'level_status': status,
        'some_flag': flag,
        'counter': counter,
        'messages': messages
    })


@login_required
def delete_step(request, step, index=1):
    step -= 1
    user = auth.get_user(request)

    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    if step < 0:
        return redirect('step', 1, 1)
    elif step >= len(modules):
        return redirect('overview')
    module = modules[step]
    module.instance(user, index - 1)[0].delete()
    if len(module.instances(user)) < module.min_items:
        meta.incomplete(step)
        if step == 6:
            try:
                employee_detail = mods.employment_details.EmploymentDetail.objects.get(user=user)
            except:
                employee_detail = ''
            if employee_detail:
                if employee_detail.is_auto_gen == True:
                    meta.incomplete(step+1)
                    employee_detail.delete()
                else:
                    meta.complete(step)
    return redirect("step", step + 1, 1)


@login_required
def list_step(request, step):
    step -= 1
    counter = 0
    user = auth.get_user(request)
    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    status = methods.level_status(request, modules, meta)
    for i in status:
        if i['counter'] > 0 and i['level'] > 1:
            counter = i['counter']
            break
        elif i['counter'] == 1:
            counter = 1
            break
    if step < 0:
        return redirect('step', 1, 1)
    elif step >= len(modules):
        return redirect('overview')
    module = modules[step]

    if module.min_items == 0 and not meta.is_complete(step):
        meta.complete(step)

    instances = module.instances(user)
    return render(request, 'list-step.html', {
        'module': module,
        'step': step + 1,
        'instances': instances,
        'num_instances': len(instances),
        'meta': meta,
        'modules': modules,
        'level_status': status,
        'counter': counter
    })


@login_required
def info(request):
    user = request.user

    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    module_map = []
    completed = []
    for i in range(len(modules)):
        module_map.append({
            'completed': meta.is_complete(i),
            'verified': meta.is_verified(i),
            'name': modules[i].model.__name__,
            'title': modules[i].title,
            'level': modules[i].level
        })
        if meta.is_complete(i):
            completed.append(modules[i].title)

    return JsonResponse({
        'id': user.id,
        'account_type': meta.account_type,
        'login': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'modules': module_map,
    })


@login_required
def download(request):
    path = request.GET.get("path")
    if not path:
        raise Http404("Could not find the requested image.")
    if not re.match(f'^kyc/user\_[0-9]+/[a-zA-Z\_0-9\-]+\.(png|pdf|jpg|jpeg)$', path):
        raise Http404("Could not find the requested image.")

    path_parts = path.split('/')
    user_id = int(path_parts[1].split('_')[1])

    user = auth.get_user(request)
    if user_id == user.id or user.is_superuser:
        with default_storage.open(path, "rb") as f:
            data = f.read()
            mime = magic.from_buffer(data, mime=True)
            return HttpResponse(data, content_type=mime)
    return redirect('/')


def resetpassword(request):
    error = ''
    form = forms.auth.ForgotPasswordForm()
    if request.method == 'POST':
        email = request.POST['email']
        form = forms.auth.ForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                user_info = User.objects.get(username=email)
                methods.forgotpassword(form, user_info, request)
                return redirect('verify-code')
            except Exception as e:
                error = str(e)
    return render(request, 'reset-password/reset-password.html', {'form': form, 'error': error})


def verify_code(request):
    error = ''
    form = forms.auth.VerifyCodeForm()
    if request.method == 'POST':
        form = forms.auth.VerifyCodeForm(request.POST)
        if form.is_valid():
            code = form.data['code']
            try:
                verified_code = mods.metadata.Metadata.objects.get(password_code=code)
                if verified_code:
                    return redirect('update-password', code)
                else:
                    error = "Try again!"
            except Exception as e:
                print(e)
                error = "Code is incorrect."
    return render(request, 'reset-password/verify-code.html', {'form': form, 'error': error})


def update_password(request, token):
    error = ''
    success = ''
    form = forms.auth.UpdatePasswordForm(label_suffix='')
    if request.method == 'POST':
        verified_code = mods.metadata.Metadata.objects.filter(password_code=token).values('user')
        if verified_code:
            form = forms.auth.UpdatePasswordForm(request.POST, label_suffix='')
            if form.is_valid():
                password = request.POST['password']
                confirm_password = request.POST['confirm_password']
                if password == confirm_password:
                    user = verified_code[0]['user']
                    user = User.objects.get(pk=user)
                    user.set_password(password)
                    user.save()
                    success = 'Password changed successfully.'
                    return redirect('login')
                else:
                    error = "Confirm password is incorrect."
        else:
            error = "Invalid token!"

    return render(request, 'reset-password/update-password.html', {'form': form, 'error': error, 'token': token})


def ifsc_api(request):
    ifsc_code = request.GET.get('ifsc_code', None)
    url = 'https://ifsc.razorpay.com/' + ifsc_code
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
    else:
        data = ''
    return JsonResponse(data, safe=False)


def pincode_api(request):
    pin_code = request.GET.get('pin_code', None)
    url = 'http://www.postalpincode.in/api/pincode/' + pin_code
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
    else:
        data = ''
    return JsonResponse(data, safe=False)


def get_criff_score(request):
    try:
        from bizcred.modules.veloce_score_master import VeloceScoreMaster
        from bizcred.modules.veloce_score import VeloceScoreMaster
        user_email = request.GET['email']
        user_criff_score = VeloceScoreMaster.objects.get(user__email=user_email)
        criff_score = user_criff_score.get_score()
        rating_value = None
        for rating in VeloceScoreMaster.objects.all():
            rating_start = Decimal(rating.start)
            rating_end = Decimal(rating.end)
            if criff_score >= rating_start and criff_score <= rating_end:
                rating_value = rating.get_veloce_rating_display()
                break
            else:
                rating_value = "N/A"
        context = {
            "status": True,
            "criff_score": criff_score,
            'rating_value': rating_value
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


@login_required
def finance_type(request):
    user = auth.get_user(request)
    form = mods.financial_details.EmploymentTypeForm(label_suffix='')
    user = auth.get_user(request)
    show_form = []
    form = mods.financial_details.EmploymentTypeForm(label_suffix='')
    check_if_finance_info_exists = False
    is_completed = mods.financial_details.EmploymentType.objects.filter(user=user, is_completed=1)
    if is_completed:
        check_if_finance_info_exists = True
        finance_detail = mods.financial_details.EmploymentType.objects.get(user=user)
        try:
            selfemployed_detail = mods.financial_details.SelfEmployedInfo.objects.get(finance_type=finance_detail)
        except ObjectDoesNotExist:
            selfemployed_detail = None
        try:
            salaried_detail = mods.financial_details.SalariedInfo.objects.get(finance_type=finance_detail)
        except ObjectDoesNotExist:
            salaried_detail = None
        form = mods.financial_details.EmploymentTypeForm(instance=finance_detail, label_suffix='')
        show_form.append(form)
        if selfemployed_detail:
            form1 = mods.financial_details.SelfEmployedInfoForm(instance=selfemployed_detail, label_suffix='')
            show_form.append(form1)

        if salaried_detail:
            form2 = mods.financial_details.SalariedInfoForm(instance=salaried_detail, label_suffix='')
            show_form.append(form2)

    if request.method == 'POST':
        form = mods.financial_details.EmploymentTypeForm(request.POST, label_suffix='')
        if form.is_valid():
            finance_type = request.POST.get('finance_type')
            data = mods.financial_details.EmploymentType(
                user=user,
                finance_type=finance_type,
                is_completed=True
            )
            data.save()
            if int(finance_type) == enums.EmploymentType.SELF_EMPLOYED.value:
                return redirect('selfemployed-info', data.pk)
            else:
                return redirect('salaried-info', data.pk)
    return TemplateResponse(request, 'finance_info/finance_type.html', {
        'form': form,
        'check_if_finance_info_exists': check_if_finance_info_exists,
        'show_form': show_form
    })


@login_required
def self_employed_info(request, id):
    form_list = []
    try:
        details = mods.financial_details.EmploymentType.objects.get(pk=id)
    except ObjectDoesNotExist:
        return redirect('finance-type')
    if request.method == 'POST':
        form = mods.financial_details.SelfEmployedInfoForm(request.POST, request.FILES, label_suffix='')
        if form.is_valid():
            methods.save_self_employed_details(form, details, request)
        return redirect('finance-type')
    else:
        form = mods.financial_details.SelfEmployedInfoForm()
    return TemplateResponse(request, 'finance_info/selfemployed_info.html', {'form': form, 'form_list': form_list})


@login_required
def salaried_info(request, id):
    form = mods.financial_details.SalariedInfoForm()
    try:
        details = mods.financial_details.EmploymentType.objects.get(pk=id)
    except ObjectDoesNotExist:
        return redirect('finance-type')
    if request.method == 'POST':
        form = mods.financial_details.SalariedInfoForm(request.POST, request.FILES, label_suffix='')
        # try:
        if form.is_valid():
            methods.save_salaried_details(form, details)
            return redirect('finance-type')
        # except Exception as e:
        #     return HttpResponse(e)

    return TemplateResponse(request, 'finance_info/salaried_info.html', {'form': form})


@csrf_exempt
def get_bank_details_by_user_id(request):
    try:
        user = User.objects.get(email=request.POST['user_email'])
        user_info = mods.bank.Bank.objects.get(user=user)
        context = {
            "status": True,
            'bank_name': user_info.bank_name,
            'ifsc_code': user_info.ifsc_code,
            'account_no': user_info.account_no
        }
        return JsonResponse(context)
    except Exception as e:
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)


def resend_otp(request):
    phone_info = mods.phone.Phone.objects.get(user=request.user)
    phone = methods.sending_sms_otp(phone_info, request.user.email)
    print("*****************", phone)
    if phone['status'] == True:
        if phone['out']:
            current_date = datetime.datetime.now().replace(tzinfo=pytz.UTC)
            out = mods.phone.Phone.objects.get(user=request.user)
            out.expiry_date = current_date
            out.otp = phone['otp']
            out.save()
        else:
            raise ValidationError("Try again!")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_previous_emi_amount(request):
    try:
        user = User.objects.filter(email=request.GET['email'])
        if user.count() > 0:
            emi_amt = mods.sanctioned_loans.SanctionedLoan.objects.filter(user=user[0])
            if emi_amt.count() > 0:
                total_emi_amt = 0
                for emi in emi_amt:
                    total_emi_amt += emi.loan_emi
                context = {
                    "status": True,
                    'emi': total_emi_amt
                }
                return JsonResponse(context)
            else:
                context = {
                    "status": False,
                    "msg": "No Data Found"
                }
                return JsonResponse(context)
        else:
            context = {
                "status": False,
                "msg": "No Data Found"
            }
            return JsonResponse(context)
    except Exception as e:
        print(e)
        context = {
            "status": False,
            "msg": str(e)
        }
        return JsonResponse(context)



class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        uid = request.GET['report_id']
        pdf = ''
        try:
            data_list = []
            data_dict = {}
            if '@' in uid:
                print("email")
                user_data = auth.models.User.objects.get(email=uid)
            else:
                user_data = auth.models.User.objects.get(id=uid)
            user_meta = user_data.metadata
            if user_meta.account_type == 1:
                crif_data = mods.crif_data.B2CReport.objects.get(user=user_data)
                data = json.dumps(crif_data.data)
                final_data = data.replace("-", "_")
                dict_data = json.loads(final_data)
                data = dict_data['B2C_REPORT']
                if data['RESPONSES']['RESPONSE']:
                    for ld in data['RESPONSES']['RESPONSE']:
                        if ld:
                            for k, v in ld['LOAN_DETAILS'].items():
                                data_dict[k] = v
                                data_list.append(data_dict)
                pdf = render_to_pdf('/crif_pdf_report/crif_individual_report.html', data)
                return HttpResponse(pdf, content_type='application/pdf')
                # return render(request, '/crif_pdf_report/crif_institution_report.html',
                #               {"data": data})
            elif user_meta.account_type == 2:
                crif_data = mods.crif_data.B2CReport.objects.get(user=user_data)
                data = json.dumps(crif_data.data)
                final_data = data.replace("-", "_")
                dict_data = json.loads(final_data)
                data = dict_data['BBC_COMMERCIAL_RESPONSE_FILE']
                phone = difflib.get_close_matches('PHONE_NUMBER', data['COMMERCIAL_CREDIT_REPORT']['COMMERCIAL_REPORT']['REQUEST'])
                month_lst = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                try:
                    trade_line = data['COMMERCIAL_CREDIT_REPORT']['COMMERCIAL_REPORT']['TRADELINES']['TRADELINE']
                    trade_line_row_list = []
                    for trade_line_item in trade_line:
                        trade_line_row_list.append(trade_line_item)
                    final_html = ''
                    for tl_list in trade_line_row_list:
                        dpd = ''
                        suit_amount = ''
                        wl_def = ''
                        dos = ''
                        suit_ref = ''
                        suit_fs = ''
                        bal_data_dict = {}
                        pay_data_dict = {}
                        if tl_list['DPD'] == '0':
                           dpd = tl_list['ASSET_CLASSIFICATION']
                        else:
                            dpd = tl_list['DPD']
                        if tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"]:
                            suit_data = ''
                            for sw in tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"]:
                                if sw == 'SUIT_AMOUNT':
                                    suit_amount = tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"][sw]
                                if sw == 'WILFUL_DEFAULTER':
                                    wl_def = tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"][sw]
                                if sw == 'DATE_OF_SUIT':
                                    dos = tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"][sw]
                                if sw == 'SUIT_FILED_STATUS':
                                    suit_fs = tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"][sw]
                                if sw == 'SUIT_REFERENCE':
                                    suit_ref = tl_list["SUIT_FILED_AND_WILFUL_DEFAULTS"][sw]
                        for dv in tl_list:
                            if dv == 'CUR_BAL_HIST':
                                for dv in methods.array_dt(tl_list[dv]):
                                    if dv[1] in bal_data_dict:
                                        bal_data_dict[dv[1]].append([dv[0], dv[2]])
                                    else:
                                        bal_data_dict[dv[1]] = [[dv[0], dv[2]]]
                            elif dv == 'PAYMENT_HISTORY':
                                for dv in methods.array_dt(tl_list[dv]):
                                    if dv[1] in pay_data_dict:
                                        pay_data_dict[dv[1]].append([dv[0], dv[2]])
                                    else:
                                        pay_data_dict[dv[1]] = [[dv[0], dv[2]]]
                        bal_html = ''
                        for dk, dv in bal_data_dict.items():
                            bal_month_array = [['Jan', ''], ['Feb', ''], ['Mar', ''], ['Apr', ''], ['May', ''], ['Jun', ''], ['Jul', ''], ['Aug', ''], ['Sep', ''], ['Oct', ''], ['Nov', ''], ['Dec', '']]
                            for m in range(len(bal_month_array)):
                                for dd in dv:
                                    if bal_month_array[m][0] == dd[0]:
                                        bal_month_array[m][1] = dd[1]
                            bal_html += '<tr><td>' + dk + '</td>' + str(methods.convert_dl_to_html(bal_month_array)) + '</tr>'
                        pay_html = ''
                        for dk, dv in pay_data_dict.items():
                            pay_month_array = [['Jan', ''], ['Feb', ''], ['Mar', ''], ['Apr', ''], ['May', ''], ['Jun', ''], ['Jul', ''], ['Aug', ''], ['Sep', ''], ['Oct', ''], ['Nov', ''], ['Dec', '']]
                            for m in range(len(pay_month_array)):
                                for dd in dv:
                                    if pay_month_array[m][0] == dd[0]:
                                        pay_month_array[m][1] = dd[1]
                            pay_html += '<tr><td>' + dk + '</td>' + str(methods.convert_dl_to_html(pay_month_array)) + '</tr>'
                        final_html += '<p style="background-color: #E6E6FA;"><b>Loan Terms For:</b>'+ tl_list['BORROWER_NAME'] +'</p><div class="container"><div class="row"><div class="col"><b style="color: #3f80ae;">Type:</b>'+ tl_list["CREDIT_FACILITY_TYPE"] +' - In '+ tl_list["ISSUED_CURRENCY"] +'</div><div class="col"><b style="color: #3f80ae;">DPD/Asset Classification:</b>' +  dpd + '</div><div class="col"><b style="color: #3f80ae;">Sanctioned Date:</b>'+ tl_list["ISSUED_CURRENCY"] +'</div></div><div class="row"><div class="col"><b style="color: #3f80ae;">Lender:</b>'+ tl_list["CREDIT_GRANTOR"] +'</div><div class="col"><b style="color: #3f80ae;">Last Payment Date:</b></div><div class="col"><b style="color: #3f80ae;">Current Balance:</b>'+ tl_list['CURRENT_BALANCE'] +'</div></div><div class="row"><div class="col"><b style="color: #3f80ae;">Account #:</b>'+ tl_list["ACCOUNT_NO"] +'</div><div class="col"><b style="color: #3f80ae;">Amount Overdue:</b>'+ tl_list["OVERDUE_AMOUNT"] +'</div><div class="col"><b style="color: #3f80ae;">Sanctioned Amount:</b>'+ tl_list["SANCTIONED_AMOUNT"] +'</div></div><div class="row"><div class="col"><b style="color: #3f80ae;">Closure Reason:</b>'+ str(tl_list["CLOSURE_REASON"]) +'</div><div class="col"><b style="color: #3f80ae;">Closed Date:</b></div><div class="col"><b style="color: #3f80ae;">Drawing Power:</b>'+ tl_list["DRAWING_POWER"] +'</div></div></div><br /><p style="color: #0f3f6b;"><b>Current Balance History (12 Months):</b></p><table class="container"><tr style="color: white; background-color: #3f80ae;"><th></th>'+ str(methods.month_list(month_lst)) +'</tr>' + bal_html + '</table><br /><p style="color: #0f3f6b;"><b>Payment History/Asset Classification:</b></p><table class="container"><tr style="color: white; background-color: #3f80ae;"><th></th>'+ str(methods.month_list(month_lst)) +'</tr>' + pay_html + '</table><br /><p style="color: #0f3f6b; border-bottom-style: solid; border-bottom-color: #a7cbe3; border-width: 1px;"><b>Suit Filed & Wilful Default</b></p><div class="row"><div class="col"><b style="color: #3f80ae;">Suit Filed Status:</b>'+ suit_fs +'</div><div class="col"><b style="color: #3f80ae;">Suit Amount:</b>'+ suit_amount +'</div><div class="col"><b style="color: #3f80ae;">Date of Suit:</b>'+ dos +'</div></div><div class="row"><div class="col"><b style="color: #3f80ae;">Suit Reference: </b>'+ suit_ref +'</div><div class="col"><b style="color: #3f80ae;">Wilful Defaulter:</b>'+ wl_def +'</div><div class="col"><b style="color: #3f80ae;">Wilful Default As On:</b></div></div><br />'
                except Exception as e:
                    print("--------------------->:", e)
                # pdf = render_to_pdf('/crif_pdf_report/crif_institution_report.html', {"data": data, "phone_list": phone, "months": month_lst, "cur_bal_his": final_html})
                # return HttpResponse(pdf, content_type='application/pdf')
                return render(request, '/crif_pdf_report/crif_institution_report.html', {"data": data, "phone_list": phone, "months": month_lst, "cur_bal_his": final_html})
        except Exception as e:
            print('Exception-------->',e)
            return HttpResponse("<h2>Your CRIF Report is not generated. Please contact administrator for any query!</hr>")

def delete_image_by_id(request):
    try:
        col_name = request.GET['name']
        col_id = request.GET['id']
        step = request.GET['step']
        col_id = col_id.split('/')
        id = col_id[0]
        model_name = col_id[1]
        model_name = model_name.split('.')
        if model_name[1] == 'address':
            address_img = mods.address.Address.objects.get(id=id).proof.delete(save=True)
        elif model_name[1] == 'identification':
            if col_name == 'pan_card':
                address_img = mods.identification.Identification.objects.get(id=id).pan_card.delete(save=True)
            if col_name == 'aadhar_card':
                address_img = mods.identification.Identification.objects.get(id=id).aadhar_card.delete(save=True)
            if col_name == 'gst_proof':
                address_img = mods.identification.Identification.objects.get(id=id).gst_proof.delete(save=True)
            if col_name == 'passport':
                address_img = mods.identification.Identification.objects.get(id=id).passport.delete(save=True)
            if col_name == 'driving_license':
                address_img = mods.identification.Identification.objects.get(id=id).driving_license.delete(save=True)
            if col_name == 'voter_id':
                address_img = mods.identification.Identification.objects.get(id=id).voter_id.delete(save=True)
            if col_name == 'utility_bill':
                address_img = mods.identification.Identification.objects.get(id=id).utility_bill.delete(save=True)
        elif model_name[1] == 'bank':
            address_img = mods.bank.Bank.objects.get(id=id).cancel_cheque.delete(save=True)
        elif model_name[1] == 'incometaxreturn':
            address_img = mods.itr.IncomeTaxReturn.objects.get(id=id).tax_return.delete(save=True)
        elif model_name[1] == 'businessfinancial':
            if col_name == 'balance_sheet':
                address_img = mods.business_financial.BusinessFinancial.objects.get(id=id).balance_sheet.delete(save=True)
            if col_name == 'pnl_statement':
                address_img = mods.business_financial.BusinessFinancial.objects.get(id=id).pnl_statement.delete(save=True)
            if col_name == 'certified_audit_report':
                address_img = mods.business_financial.BusinessFinancial.objects.get(id=id).certified_audit_report.delete(
                    save=True)
        elif model_name[1] == 'employmentdetail':
            if col_name == 'appointment_letter':
                address_img = mods.employment_detail.EmploymentDetail.objects.get(id=id).appointment_letter.delete(
                    save=True)
            if col_name == 'salary_slip':
                address_img = mods.employment_detail.EmploymentDetail.objects.get(id=id).salary_slip.delete(save=True)
        elif model_name[1] == 'bankstatement':
            address_img = mods.bank_statement.BankStatement.objects.get(id=id).statement.delete(save=True)
        elif model_name[1] == 'sanctionedloan':
            if col_name == 'letter':
                address_img = mods.sanctioned_loans.SanctionedLoan.objects.get(id=id).letter.delete(save=True)
            if col_name == 'lender_noc':
                address_img = mods.sanctioned_loans.SanctionedLoan.objects.get(id=id).lender_noc.delete(save=True)
        user = auth.get_user(request)
        meta = user.metadata
        meta.incomplete(int(step)-1)
    except Exception as e:
        print("***************************", e)

    context = {
        "status": True,
        "id": col_id,
        "name": col_name
    }
    return JsonResponse(context)


def get_score_by_id(request):
    try:
        coborrower_id = request.GET['coborrower_id']
        borrower_id = request.GET['borrower_id']
        borrower_data = mods.veloce_score_master.VeloceScoreMaster.objects.get(user__email=borrower_id)
        coborrower_data = mods.veloce_score_master.VeloceScoreMaster.objects.get(user__email=coborrower_id)
        context = {
            "status": True,
            # 'crif_score': 100,
            'coborrower_total': coborrower_data.get_score(),
            'coborrower_crif': coborrower_data.crif_score,
            'borrower_crif': borrower_data.crif_score,
            'borrower_total': borrower_data.get_score()
        }
        return JsonResponse(context)
    except Exception as e:
        print(e)
        context = {
            'status': False,
            'msg': str(e)
        }
        return JsonResponse(context)

def get_comp_det_by_id(request):
    try:
        # print(request.GET)
        email = request.GET['email']
        gen_data = mods.metadata.Metadata.objects.get(user__email=email)
        name = ''
        if gen_data.account_type == 2:
            name = gen_data.org_name
        else:
            name = gen_data.user.first_name + ' ' + gen_data.user.last_name
        context = {
            'data': name,
            'status': True,
            'acc_type': gen_data.account_type
        }
        return JsonResponse(context)
    except Exception as e:
        print(e)
        context = {
            'status': False,
            'msg': str(e)
        }
        return JsonResponse(context)


def xml_render(request):
    report_id, order_id, RESPONSEDTTM = methods.crif_score_institution(request)
    data = methods.crif_score_institution_2(request, report_id, order_id, RESPONSEDTTM)

    return HttpResponse('Hiiiiiiii')

def check_updated_module_approved(request):
    user_email = request.GET['uid']
    user = auth.models.User.objects.get(email=user_email)
    meta = user.metadata
    modules = form_map.FORM_MAP[meta.account_type]
    count = 0
    incomplete_level = []
    not_verified_level = []
    for i in range(len(modules)):
        if not meta.is_complete(i):
            count += 1
            incomplete_level.append(modules[i].level)
        if meta.is_complete(i) and not meta.is_verified(i):
            count += 1
            not_verified_level.append(modules[i].level)
    if count > 0:
        print("Working", incomplete_level)
        return JsonResponse({'status': False, 'incomplete_level': incomplete_level, 'not_verified_level': not_verified_level})
    else:
        print("Working", incomplete_level)
        return JsonResponse({'status': True, 'incomplete_level': incomplete_level, 'not_verified_level': not_verified_level})


def user_details_by_id(request):
    user_email = request.GET['email']
    user = auth.models.User.objects.get(email=user_email)
    meta = user.metadata
    general = mods.general.General.objects.get(user=user)
    print("____________", general.gender)
    general.gender = enums.Gender(general.gender).name
    general.marital_status = enums.MaritalStatus(general.marital_status).name
    general_data = serialize("json", [general], fields=('father_husband_no', 'org_name', 'birthdate', 'gender', 'marital_status'))
    phone = mods.phone.Phone.objects.get(user=user)
    address = mods.address.Address.objects.get(user=user)
    address.state = enums.IndiaStates(address.state).name
    address_data = serialize("json", [address], fields=('unit_number', 'street_address', 'tel_number', 'pin_code', 'city', 'state'))
    data = {}
    if meta.account_type == 1:
        identification = mods.identification.Identification.objects.get(user=user)
        identification_data = serialize("json", [identification], fields=('pan_number', 'aadhar_number', 'gst_number'))
        data = {
            'name': user.first_name + ' ' + user.last_name,
            'general': general_data,
            'phone': phone.phone_number,
            'address': address_data,
            'identification': identification_data,
            'acc_type': 1
        }
    else:
        company = mods.company_details.CompanyDetails.objects.get(user=user)
        company_data = serialize("json", [company], fields=('org_name', 'org_type', 'company_register_no', 'soc'))
        add_company_details = mods.additional_company_details.AdditionalCompanyDetails.objects.get(user=user)
        add_company_details_data = serialize("json", [add_company_details], fields=('pan_number', 'udyog_aadhar_number', 'gst_number'))
        data = {
            'name': user.first_name + ' ' + user.last_name,
            'company': company_data,
            'general': general_data,
            'phone': phone.phone_number,
            'address': address_data,
            'add_company_details': add_company_details_data,
            'acc_type': 2
        }
    return JsonResponse({'data': data})


def get_field_and_value_dict(model,dict_name):
    dict_name = dict()
    list_display = [field.name for field in model._meta.get_fields()]
    for field in list_display:
        field_object = model._meta.get_field(field)
        field_value = field_object.value_from_object(model)
        dict_name[field_object.name] = str(field_value) if  field_value != '' else '-'
    dict_name['user'] = str(model.user.username)
    return dict_name


@login_required
def user_info(request):
    address_data = []
    # get user to get user data
    matadata = models.metadata.Metadata.objects.filter(account_type = 4)
    dealer_email_list =[]
    final_list = []
    for mata in matadata :
        user_final_dict ={}
        single_dealer_data_list = []
        single_dealer_data_dict = {}
        request_user = mata.user

        # user details (done)
        try :
            model = User.objects.get(pk = request_user.pk)
            dict_name = {
                'id' : model.id,
                'username' : model.username,
                'email' : model.username,
                'first_name' : model.first_name,
                'last_name' : model.last_name,
            }
            single_dealer_data_dict['User'] = dict_name

        except:
            pass
        
        # get matadata details(done)
        try:
            model = models.metadata.Metadata.objects.get(user = request_user)
            dict_name = 'Matadata'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict
        except :
            pass
            

        # get phone details(done)
        try :
            model = models.phone.Phone.objects.get(user = request_user)
            dict_name = 'Phone'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass


        # general details get (done)
        try :
            model = models.general.General.objects.get(user = request_user)
            dict_name = 'General'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['education_level'] = enums.EducationLevel(model.education_level).name
            final_dict['gender'] = enums.Gender(model.gender).name
            final_dict['net_monthly_income'] = enums.MonthlyIncome(model.net_monthly_income).name
            final_dict['marital_status'] = enums.MaritalStatus(model.marital_status).name
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # AdditionalCompanyDetails details (done)
        try :
            model = models.additional_company_details.AdditionalCompanyDetails.objects.get(user = request_user)
            dict_name = 'AdditionalCompanyDetails'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # AuthAdditionalCompanyDetails details (done)
        try :
            model = models.additional_company_details.AuthAdditionalCompanyDetails.objects.get(user = request_user)
            dict_name = 'AuthAdditionalCompanyDetails'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # company details (done)
        try:
            model = models.company_details.CompanyDetails.objects.get(user = request_user)
            dict_name = 'CompanyDetails'
            dict = {
                    'user' : model.user.username,
                    'org_name' : model.org_name if  model.org_name != '' else '-',
                    'org_website' : model.org_website  if model.org_website != '' else '-',
                    'org_type': model.org_type if model.org_type != '' else '-',
                    'company_register_no': model.company_register_no if model.company_register_no != '' else '-',
                    'soc': model.soc if model.soc != '' else '-',
                    'year': model.year if model.year != '' else '-',
                    'month': model.month if model.month != '' else '-',
                    'reject_reason': model.reject_reason if model.reject_reason != '' else '-',
            }
            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass


        # address details (done)
        try:
            model = models.address.Address.objects.get(user = request_user)
            dict_name = 'Address'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['state'] = enums.IndiaStates(model.state).name
            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass

        # bank statement details (done)
        try:
            for_model = models.bank_statement.BankStatement.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'BankStatement'
                for_dict_name = 'BankStatement'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # bank details (done)
        try:
            model = models.bank.Bank.objects.get(user = request_user)
            dict_name = 'Bank'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['bank_acc_type'] = enums.BankAccountType(model.bank_acc_type).name

            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass

        # BusinessFinancial details (done)
        try:
            for_model = models.business_financial.BusinessFinancial.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'BusinessFinancial'
                for_dict_name = 'BusinessFinancial'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # employment details (done)
        try :
            model = models.employment_details.EmploymentDetail.objects.get(user = request_user)
            dict_name = 'EmploymentDetail'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # IncomeTaxReturn details (done)
        try:
            for_model = models.itr.IncomeTaxReturn.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'IncomeTaxReturn'
                for_dict_name = 'IncomeTaxReturn'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # Sanctioned loans details (done)
        try :
            model = models.sanctioned_loans.SanctionedLoan.objects.get(user = request_user)
            dict_name = 'SanctionedLoan'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict
    
        except:
            pass

        user = request_user

        meta = user.metadata
        modules = form_map.FORM_MAP[meta.account_type]
        module_map = []
        completed = []
        for i in range(len(modules)):
            module_map.append({
                'completed': meta.is_complete(i),
                'verified': meta.is_verified(i),
                'name': modules[i].model.__name__,
                'title': modules[i].title,
                'level': modules[i].level
            })
            if meta.is_complete(i):
                completed.append(modules[i].title)

        user_level_data={
            'id': user.id,
            'account_type': meta.account_type,
            'login': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'modules': module_map,
        }
        single_dealer_data_dict['user_level_data'] = user_level_data
        single_dealer_data_list.append(single_dealer_data_dict)
        final_list.append(single_dealer_data_list)
        dealer_email_list.append(request_user)
   
    return JsonResponse({'user_data':final_list})


def company_info(request):
    address_data = []
    # get user to get user data
    matadata = models.metadata.Metadata.objects.filter(account_type = 2)
    dealer_email_list =[]
    final_list = []
    for mata in matadata :
        user_final_dict ={}
        single_dealer_data_list = []
        single_dealer_data_dict = {}
        request_user = mata.user

        # user details (done)
        try :
            model = User.objects.get(pk = request_user.pk)
            dict_name = {
                'id' : model.id,
                'username' : model.username,
                'email' : model.username,
                'first_name' : model.first_name,
                'last_name' : model.last_name,
            }
            single_dealer_data_dict['User'] = dict_name
        except:
            pass

        # get matadata details(done)
        try:
            model = models.metadata.Metadata.objects.get(user = request_user)
            dict_name = 'Matadata'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict
        except :
            pass
            

        # get phone details(done)
        try :
            model = models.phone.Phone.objects.get(user = request_user)
            dict_name = 'Phone'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass


        # general details get (done)
        try :
            model = models.general.General.objects.get(user = request_user)
            dict_name = 'General'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['education_level'] = enums.EducationLevel(model.education_level).name
            final_dict['gender'] = enums.Gender(model.gender).name
            final_dict['net_monthly_income'] = enums.MonthlyIncome(model.net_monthly_income).name
            final_dict['marital_status'] = enums.MaritalStatus(model.marital_status).name
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # AdditionalCompanyDetails details (done)
        try :
            model = models.additional_company_details.AdditionalCompanyDetails.objects.get(user = request_user)
            dict_name = 'AdditionalCompanyDetails'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # AuthAdditionalCompanyDetails details (done)
        try :
            model = models.additional_company_details.AuthAdditionalCompanyDetails.objects.get(user = request_user)
            dict_name = 'AuthAdditionalCompanyDetails'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # company details (done)
        try:
            model = models.company_details.CompanyDetails.objects.get(user = request_user)
            dict_name = 'CompanyDetails'
            dict = {
                    'user' : model.user.username,
                    'org_name' : model.org_name if  model.org_name != '' else '-',
                    'org_website' : model.org_website  if model.org_website != '' else '-',
                    'org_type': model.org_type if model.org_type != '' else '-',
                    'company_register_no': model.company_register_no if model.company_register_no != '' else '-',
                    'soc': model.soc if model.soc != '' else '-',
                    'year': model.year if model.year != '' else '-',
                    'month': model.month if model.month != '' else '-',
                    'reject_reason': model.reject_reason if model.reject_reason != '' else '-',
            }
            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass

        # address details (done)
        try:
            model = models.address.Address.objects.get(user = request_user)
            dict_name = 'Address'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['state'] = enums.IndiaStates(model.state).name
            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass

        # bank statement details (done)
        try:
            for_model = models.bank_statement.BankStatement.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'BankStatement'
                for_dict_name = 'BankStatement'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # bank details (done)
        try:
            model = models.bank.Bank.objects.get(user = request_user)
            dict_name = 'Bank'
            final_dict = get_field_and_value_dict(model,dict_name)
            final_dict['bank_acc_type'] = enums.BankAccountType(model.bank_acc_type).name

            single_dealer_data_dict[dict_name] = final_dict
        except:
            pass

        # BusinessFinancial details (done)
        try:
            for_model = models.business_financial.BusinessFinancial.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'BusinessFinancial'
                for_dict_name = 'BusinessFinancial'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # employment details (done)
        try :
            model = models.employment_details.EmploymentDetail.objects.get(user = request_user)
            dict_name = 'EmploymentDetail'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict

        except:
            pass

        # IncomeTaxReturn details (done)
        try:
            for_model = models.itr.IncomeTaxReturn.objects.filter(user = request_user)
            lst=[]
            for model in range(len(for_model)):
                dict_name = 'IncomeTaxReturn'
                for_dict_name = 'IncomeTaxReturn'+ str(model+1)
                model = for_model[model]
                final_dict = get_field_and_value_dict(model,dict_name)
                dict = {}
                dict[for_dict_name] = final_dict
                lst.append(dict)
            single_dealer_data_dict[dict_name] = lst
        except:
            pass

        # Sanctioned loans details (done)
        try :
            model = models.sanctioned_loans.SanctionedLoan.objects.get(user = request_user)
            dict_name = 'SanctionedLoan'
            final_dict = get_field_and_value_dict(model,dict_name)
            single_dealer_data_dict[dict_name] = final_dict
    
        except:
            pass

        user = request_user

        meta = user.metadata
        modules = form_map.FORM_MAP[meta.account_type]
        module_map = []
        completed = []
        for i in range(len(modules)):
            module_map.append({
                'completed': meta.is_complete(i),
                'verified': meta.is_verified(i),
                'name': modules[i].model.__name__,
                'title': modules[i].title,
                'level': modules[i].level
            })
            if meta.is_complete(i):
                completed.append(modules[i].title)

        user_level_data={
            'id': user.id,
            'account_type': meta.account_type,
            'login': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'modules': module_map,
        }
        single_dealer_data_dict['user_level_data'] = user_level_data
        single_dealer_data_list.append(single_dealer_data_dict)
        final_list.append(single_dealer_data_list)
    return JsonResponse({'user_data':final_list})