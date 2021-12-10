from django.db import models
from django.contrib.auth.models import User
from bizcred import modules
from bizcred.forms import base
from django import forms

SCORE = 0


class VeloceScoreMaster(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    crif_score = models.DecimalField(
        max_digits=22,
        decimal_places=2,
        null=True,
        blank=True
    )
    mca_default = models.BooleanField(default=False)

    gst_default = models.BooleanField(default=False)

    criminal_civil_case = models.BooleanField(default=False)

    is_address_checked = models.BooleanField(default=False)

    own_house = models.BooleanField(default=False)

    de_ratio = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True
    )
    current_ratio = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True
    )
    ebitda_percentage = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True
    )

    int_cov_ratio = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Interest Coverage Ratio",
        null=True,
        blank=True
    )
    credit_rating = models.CharField(
        max_length=5,
        null=True,
        blank=True
    )
    is_pan_verified = models.BooleanField(default=False)

    is_gst_verified = models.BooleanField(default=False)

    is_adhaar_verified = models.BooleanField(default=False)

    cheque_bounced = models.BooleanField(default=False)

    bank_comfort_letter = models.BooleanField(default=False)

    credit_manage_score = models.DecimalField(
        max_digits=22,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_score = models.DecimalField(
        max_digits=22,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.email

    # def fun_get_score(self,p_para,p_value  *args)
    #         SCORE = self.crif_score

    def get_score(self):
        SCORE = self.crif_score
        try:
            if self.mca_default == 0:
                SCORE = SCORE + 100
            else:
                SCORE = SCORE - 50

            if self.gst_default == 0:
                SCORE = SCORE + 100
            else:
                SCORE = SCORE - 100

            if self.criminal_civil_case == 0:
                SCORE = SCORE + 100
            else:
                SCORE = SCORE - 200

            if self.is_address_checked == 0:
                SCORE = SCORE - 200
            else:
                SCORE = SCORE + 100

            if self.own_house == 0:
                SCORE = SCORE - 100
            else:
                SCORE = SCORE + 100

            if self.de_ratio != None:
                if self.de_ratio < 1.5:
                    SCORE = SCORE + 100
                else:
                    SCORE = SCORE - 200
            else:
                pass
            if self.current_ratio != None:
                if self.current_ratio < 1.75:
                    SCORE = SCORE - 100
                else:
                    SCORE = SCORE + 100
            else:
                pass
            if self.ebitda_percentage != None:
                if self.ebitda_percentage < 12:
                    SCORE = SCORE - 100
                else:
                    SCORE = SCORE + 100
            else:
                pass
            if self.int_cov_ratio != None:
                if self.int_cov_ratio < 1.25:
                    SCORE = SCORE - 100
                else:
                    SCORE = SCORE + 100
            else:
                pass
            if self.credit_rating != None:
                SCORE = SCORE + int(self.credit_rating)

            if self.is_pan_verified == 1 and self.is_gst_verified == 1 and self.is_adhaar_verified == 1:
                SCORE = SCORE + 100
            else:
                SCORE = SCORE - 500

            if self.cheque_bounced == 0:
                SCORE = SCORE + 50
            else:
                SCORE = SCORE - 100

            if self.bank_comfort_letter == 0:
                SCORE = SCORE - 50
            else:
                SCORE = SCORE + 50
            if self.credit_manage_score != None:
                SCORE = SCORE + self.credit_manage_score
        except Exception as e:
            if self.credit_manage_score != None:
                SCORE = SCORE + self.credit_manage_score
            print("++++++++++++++", SCORE)
        except Exception as e:
            SCORE = SCORE
            print("-----------------------", e, SCORE)
        return SCORE


class VeloceScoreMasterForm(forms.ModelForm):
    class Meta:
        model = VeloceScoreMaster
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VeloceScoreMasterForm, self).__init__(*args, **kwargs)
        print(self)
        self.fields['crif_score'].widget.attrs['readonly'] = True
        self.fields['user'].widget.widget.attrs['readonly'] = True
        # veloce = modules.veloce_score_master.VeloceScoreMaster.objects.get(user_id=2)
        # total_score = veloce.get_score()
        # print('total_score --->',total_score)
        # self.initial['total_score'] = total_score
        self.fields['total_score'].widget.attrs['readonly'] = True