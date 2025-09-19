from rest_framework import serializers
from django.conf import settings

from .models import (
    Partner,
    PartnerDocument,
    PartnerProfile,
    StatusHistory,
    RiskLevelHistory,
    PartnerDepartment,
    Project,
    ProjectPartner,
    MOU,
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
    file = serializers.FileField(write_only=True, required=False)
    file_url = serializers.URLField(required=False)

    class Meta:
        model = PartnerDocument
        fields = ["id", "file_type", "file", "file_url", "uploaded_by", "uploaded_at"]

    def validate(self, attrs):
        # Custom validation logic
        if not attrs.get("file") and not attrs.get("file_url"):
            raise serializers.ValidationError("You must provide a file or a file_url.")

        return attrs

    def create(self, validated_data):
        file = validated_data.pop("file", None)

        if file:
            from django.core.files.storage import default_storage

            path = default_storage.save(f"partner_documents/{file.name}", file)
            validated_data["file_url"] = default_storage.url(path)

        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)


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


class PartnerDepartmentSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = PartnerDepartment
        fields = ["id", "partner", "department", "assigned_at"]
        read_only_fields = ["id", "partner", "assigned_at"]


class PartnerDepartmentDetailSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()

    class Meta:
        model = PartnerDepartment
        fields = ["id", "department", "assigned_at"]

    def get_department(self, obj):
        return {"id": str(obj.department.id), "name": obj.department.name}


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PartnershipProjectSerializer(serializers.ModelSerializer):
    # Nested project display (optional)
    project_name = serializers.ReadOnlyField(source="project.name")
    partner_name = serializers.ReadOnlyField(source="partner.name")

    class Meta:
        model = ProjectPartner
        fields = [
            "id",
            "project",
            "project_name",
            "partner",
            "partner_name",
            "role",
            "contribution",
            "start_date",
            "end_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MOUSerializer(serializers.ModelSerializer):

    class Meta:
        model = MOU

        fields = [
            "id",
            "project",  # FK: project ID
            "partner",  # FK: partner ID
            "title",
            "description",
            "start_date",
            "end_date",
            "status",
            "document_url",  # read-only
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "document_url", "created_at", "updated_at"]
