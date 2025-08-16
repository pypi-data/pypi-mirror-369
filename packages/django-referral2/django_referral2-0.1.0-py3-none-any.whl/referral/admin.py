from django.contrib import admin
from .models import ReferralAttribution, Reward, ReferralClick, ReferralCode

# Register your models here.
admin.site.register(ReferralCode)
admin.site.register(ReferralClick)
admin.site.register(ReferralAttribution)
admin.site.register(Reward)