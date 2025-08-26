from rest_framework import serializers
from django.conf import settings

from .models import (
    Partner,
    PartnerDocument,
    PartnerProfile,
    StatusHistory,
    RiskLevelHistory,
    PartnerDepartment,
)
from users.models import Department

User = settings.AUTH_USER_MODEL


# ----------------------
# PartnerProfileSerializer
# ----------------------


class PartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerProfile
        fields = [
            "id",
            "registration_number",
            "tax_number",
            "contact_address",
            "contact_phone",
            "contact_email",
            "ownership_structure",
            "bank_details",
            "organization_type",
            "legal_history",
            "social_background",
            "financial_stability",
            "reputation",
            "esg_policies",
            "documents",
        ]
        read_only_fields = ["id", "partner"]


# ----------------------
# PartnerDocumentSerializer
# ----------------------
class PartnerDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)  # shows username

    class Meta:
        model = PartnerDocument
        fields = ["id", "file_type", "file_url", "uploaded_by", "uploaded_at"]


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StatusHistory
        fields = ["id", "old_status", "new_status", "changed_by", "changed_at"]


class RiskLevelHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RiskLevelHistory
        fields = ["id", "old_risk", "new_risk", "changed_by", "changed_at"]


class PartnerSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    departments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "type",
            "status",
            "risk_level",
            "created_by",
            "departments",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return Partner.objects.create(created_by=user, **validated_data)


# ----------------------
# Nested Serializer: Partner with Profile & Documents
# ----------------------
class PartnerDetailSerializer(serializers.ModelSerializer):
    profile = PartnerProfileSerializer(read_only=True)
    documents = PartnerDocumentSerializer(many=True, read_only=True)
    status_history = StatusHistorySerializer(many=True, read_only=True)
    risk_history = RiskLevelHistorySerializer(many=True, read_only=True)
    departments = serializers.StringRelatedField(many=True)

    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "type",
            "status",
            "risk_level",
            "created_by",
            "departments",
            "profile",
            "documents",
            "status_history",
            "risk_history",
            "created_at",
            "updated_at",
        ]
