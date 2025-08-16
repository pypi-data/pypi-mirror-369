from rest_framework import serializers
from .models import ReferralCode, ReferralClick, ReferralAttribution


class ReferralCodeSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ReferralCode
        fields = ("id", "code", "url", "created_at", "expires_at", "meta")


    def get_url(self, obj):
        request = self.context.get("request")
        host = request.get_host() if request else "example.com"
        scheme = "https"
        return f"{scheme}://{host}/referral/r/{obj.code}"


class ClaimSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=64)
