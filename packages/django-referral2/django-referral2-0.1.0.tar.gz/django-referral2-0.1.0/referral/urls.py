from django.urls import path
from .views import GenerateReferralView, referral_redirect_view, ClaimReferralView

urlpatterns = [
    path("", GenerateReferralView.as_view(), name="generate-referral"),
    path("r/<str:code>/", referral_redirect_view, name="referral-redirect"),
    path("claim/", ClaimReferralView.as_view(), name="claim-referral"),
]
