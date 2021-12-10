from django.contrib import admin
from bizcred import form_map
from bizcred import models
from bizcred.modules.veloce_score_master import VeloceScoreMasterForm

# Register your models here.
for user in form_map.FORM_MAP:
    for module in form_map.FORM_MAP[user]:
        try:
            admin.site.register(module.model)
        except:
            pass


class VeloceScoreMasterAdmin(admin.ModelAdmin):
    form = VeloceScoreMasterForm


admin.site.register(models.metadata.Metadata)
admin.site.register(models.veloce_score.VeloceScore)
admin.site.register(models.veloce_score_master.VeloceScoreMaster, VeloceScoreMasterAdmin)
admin.site.register(models.finance_offer_detail.FinanceOfferDetail)
# admin.site.register(models.financial_details.EmploymentType)
# admin.site.register(models.financial_details.SelfEmployedInfo)
# admin.site.register(models.financial_details.SalariedInfo)
admin.site.register(models.v_score_approval_matrix.VeloceScoreApprovalMatrix)
admin.site.register(models.crif_data.B2CReport)
admin.site.register(models.level_email.LevelEmail)
admin.site.register(models.aadhar.Aadhar)
