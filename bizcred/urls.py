from . import views
from django.urls import path, include

urlpatterns = [
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/login/', views.login, name='login'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/change-password/', views.change_password, name='change-password'),
    path('accounts/info/', views.info),

    # ravi
    path('user/info/', views.user_info),
    path('company/info/', views.company_info),

    path('resend-otp/', views.resend_otp, name="resend_otp"),

    path('admin/profiles/', views.admin_profiles, name='list-profiles'),
    path('admin/profiles/<int:uid>', views.admin_view, name='view-profile'),
    path('admin/reject/<int:uid>/<int:step>', views.admin_reject, name='reject-profile'),

    path('step/<int:step>/<int:substep>', views.profile_step, name='step'),
    path('delete-step/<int:step>/<int:index>', views.delete_step, name='delete-step'),
    path('step/<int:step>/<int:substep>/<int:index>', views.profile_step, name='index-step'),
    path('list-step/<int:step>', views.list_step, name='list-step'),

    path('overview', views.overview, name='overview'),
    path('', views.overview),
    path('download', views.download),
    path('bank/ifsc/', views.ifsc_api, name='ifsc-api'),
    path('address/pincode/',views.pincode_api, name='pincode-api'),
    path('accounts/password_reset/', views.resetpassword, name='password_reset'),
    path('accounts/verify-code/', views.verify_code, name='verify-code'),
    path('account/update-password/<slug:token>/', views.update_password, name='update-password'),
    path('get-user-criff-score/', views.get_criff_score, name='get_criff_score'),
    #Finance Information
    path('finance-info', views.finance_type, name='finance-type'),
    path('finance-info/self_employed/<int:id>', views.self_employed_info, name='selfemployed-info'),
    path('finance-info/salaried/<int:id>', views.salaried_info, name='salaried-info'),
    path('get-bank-details_by-user-id/', views.get_bank_details_by_user_id, name='get_bank_details_by_user_id'),
    path('get-total-emi', views.get_previous_emi_amount, name='get_previous_emi_amount'),
    path('xml_render', views.xml_render, name='xml_render'),
    path('pdf_report', views.GeneratePdf.as_view(), name='pdf_report'),
    # path('veloce_pdf_report', views.GenerateVelocePdf.as_view(), name='veloce_pdf_report'),
    path('delete-image-by-id/', views.delete_image_by_id, name='delete_image_by_id'),
    path('get-score-by-id/', views.get_score_by_id, name='get-score-by-id'),
    path('get-comp-det-by-id/', views.get_comp_det_by_id, name='get-comp-det-by-id'),
    path('check-updated-module-approved/', views.check_updated_module_approved, name='check-updated-module-approved'),
    path('user-details-by-id/', views.user_details_by_id, name='user-details-by-id'),
]
