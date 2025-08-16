from django.shortcuts import get_object_or_404, redirect
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ReferralCode, ReferralClick, ReferralAttribution, Reward
from .serializers import ReferralCodeSerializer, ClaimSerializer

# Generate or get referral (authenticated)
class GenerateReferralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Generate or retrieve referral code",
        operation_description="If the user already has a referral code, it returns that. Otherwise, it generates a new one.",
        tags=["Referral"],
        request_body=ReferralCodeSerializer,
        responses={
            200: ReferralCodeSerializer,
            201: ReferralCodeSerializer,
            400: "Bad Request"
        }
        
    )
    def post(self, request):
        # Check if a referral code already exists for this user
        code = ReferralCode.objects.filter(owner=request.user).first()
        if code:
            serializer = ReferralCodeSerializer(code, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Otherwise, create a new code
        code = ReferralCode(owner=request.user)
        code.save()
        serializer = ReferralCodeSerializer(code, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# Redirect endpoint (public). Records click then redirects to signup/landing.
def referral_redirect_view(request, code):
    # get code or 404
    rc = get_object_or_404(ReferralCode, code=code)
    # record click (non-blocking if using async log/queue)
    ReferralClick.objects.create(
        referral=rc,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
        cookie_id=request.COOKIES.get("ref_cookie")
    )
    # set cookie so signup can pick it up if the user navigates
    response = redirect("signup")  # change to your sign-up URL
    response.set_cookie("ref_code", code, max_age=60 * 60 * 24 * 30)  # 30 days
    return response

# Claim endpoint — attach referral during/after signup
class ClaimReferralView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # called after user creation or during flow

    @swagger_auto_schema(
        operation_summary="Claim referral code",
        operation_description="Claim a referral code to attribute the user to a referral. ",
        tags=["Referral"],
        request_body=ClaimSerializer,
        responses={
            200: openapi.Response("Referral claimed successfully"),
            400: "Invalid code",
            409: "Already claimed",
            202: "Pending manual review"
        }
    )
    def post(self, request):
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"].lower().strip()
        # basic checks
        try:
            rc = ReferralCode.objects.get(code=code)
        except ReferralCode.DoesNotExist:
            return Response({"detail": "invalid code"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent self-referral
        if rc.owner_id == request.user.id:
            return Response({"detail": "self-referral not allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Atomic: create attribution if not exists
        try:
            with transaction.atomic():
                # ensure one-to-one constraint: ReferralAttribution uses OneToOneField for referred_user
                attrib = ReferralAttribution.objects.create(
                    referral=rc,
                    referred_user=request.user,
                    status=ReferralAttribution.STATUS_PENDING,
                    meta={"claimed_ip": request.META.get("REMOTE_ADDR")}
                )
        except IntegrityError:
            # Already claimed (idempotent)
            existing = getattr(request.user, "ref_attribution", None)
            if existing:
                return Response({"detail": "already claimed", "status": existing.status}, status=status.HTTP_200_OK)
            return Response({"detail": "could not claim"}, status=status.HTTP_409_CONFLICT)

        # Basic fraud checks (example): if suspicious, mark for manual review
        # (replace with real checks: device fingerprinting, disposable email, ip reputation)
        suspicious = False
        if request.META.get("REMOTE_ADDR") == rc.owner.last_login_ip if hasattr(rc.owner, "last_login_ip") else False:
            suspicious = True

        if suspicious:
            attrib.status = ReferralAttribution.STATUS_MANUAL
            attrib.save(update_fields=["status"])
            return Response({"detail": "pending manual review"}, status=status.HTTP_202_ACCEPTED)

        # Approve and enqueue reward
        attrib.status = ReferralAttribution.STATUS_APPROVED
        attrib.approved_at = timezone.now()
        attrib.save(update_fields=["status", "approved_at"])

        # create reward record (processing async is recommended)
        reward = Reward.objects.create(attribution=attrib, type="credit", amount=5.00)
        # use the background task queue to handle reward issuance
        reward.issued = True
        reward.issued_at = timezone.now()
        reward.save(update_fields=["issued", "issued_at"])

        # TODO: notify owner (email/push) or credit wallet via Wallet/Payments service

        return Response({"detail": "referral attributed", "reward": {"type": reward.type, "amount": str(reward.amount)}}, status=status.HTTP_200_OK)
