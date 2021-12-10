from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from bizcred import enums


def set_bit(arr, x):
    return arr | (1 << x)


def unset_bit(arr, x):
    return arr & ~(1 << x)


def isset_bit(arr, x):
    return (arr & (1 << x)) > 0


class Metadata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    account_type = models.SmallIntegerField(
        choices=enums.to_choices(enums.AccountType),
        default=1
    )
    org_name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    updated_at = models.DateField(auto_now=True)
    changelog = models.IntegerField(default=0)
    completion = models.IntegerField(default=0)

    profile_reviewed = models.IntegerField(default=0)
    profile_verified = models.IntegerField(default=0)
    is_crif_generated = models.BooleanField(default=False)
    reject_reason = models.TextField(default='')
    password_code = models.TextField(default='', blank=True)

    # @property
    def __str__(self):
        return self.user.email

    def review(self, step):
        self.profile_reviewed = set_bit(self.profile_reviewed, step)
        self.changelog = unset_bit(self.changelog, step)
        if self.profile_reviewed == self.profile_verified:
            self.reject_reason = ''

    def change(self, step):
        self.changelog = set_bit(self.changelog, step)
        self.updated_at = datetime.now()
        self.profile_verified = unset_bit(self.profile_verified, step)
        self.profile_reviewed = unset_bit(self.profile_reviewed, step)

    def approve(self, step):
        self.profile_verified = set_bit(self.profile_verified, step)
        self.review(step)
        self.save()

    def reject(self, step, reject_reason=''):
        self.profile_verified = unset_bit(self.profile_verified, step)
        self.review(step)
        self.reject_reason = reject_reason
        self.save()

    def complete(self, step):
        print("Completed", step)
        self.completion = set_bit(self.completion, step)
        self.change(step)
        self.save()

    def incomplete(self, step):
        self.completion = unset_bit(self.completion, step)
        self.change(step)
        self.save()

    def is_complete(self, step):
        return isset_bit(self.completion, step)

    def is_verified(self, step):
        return isset_bit(self.profile_verified, step)

    def get_status(self, step):
        # print('metadata stepsssssss',self,step)
        if not self.is_complete(step):
            return 'Incomplete'
        elif not isset_bit(self.profile_reviewed, step):
            return 'Pending Review'
        elif not isset_bit(self.profile_verified, step):
            return 'Rejected'
        else:
            return 'Approved'

    def equals_mask(self, mask):
        return (self.completion & mask) == mask
