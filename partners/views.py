from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Partner,
    PartnerDocument,
    PartnerProfile,
    StatusHistory,
    RiskLevelHistory,
)
from rest_framework.decorators import action
from .serializers import (
    PartnerDocumentSerializer,
    PartnerSerializer,
    PartnerDetailSerializer,
    PartnerProfileSerializer,
    StatusHistorySerializer,
    RiskLevelHistorySerializer,
)
from rest_framework.response import Response

from .permissions import IsSysAdminOrDepartmentUser


class PartnerViewSet(viewsets.ModelViewSet):
    """
    Partner CRUD:
    - POST → create partner
    - GET → list partners
    - GET /id → retrieve partner with nested info
    - PUT/PATCH → update partner
    - DELETE → soft delete
    """

    queryset = Partner.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["type", "status", "risk_level"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "updated_at"]

    permission_classes = [IsSysAdminOrDepartmentUser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PartnerDetailSerializer
        return PartnerSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        # Soft delete: mark status as suspended instead of deleting
        instance.status = "suspended"
        instance.save()

    # --------------------------
    @action(detail=True, methods=["get", "post", "put", "patch"], url_path="profile")
    def profile(self, request, pk=None):
        partner = self.get_object()

        # GET
        if request.method == "GET":
            try:
                serializer = PartnerProfileSerializer(partner.profile)
                return Response(serializer.data)
            except PartnerProfile.DoesNotExist:
                return Response(
                    {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
                )

        # POST
        elif request.method == "POST":
            if hasattr(partner, "profile"):
                return Response(
                    {"detail": "Profile already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = PartnerProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(partner=partner)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # PUT/PATCH
        elif request.method in ["PUT", "PATCH"]:
            try:
                profile = partner.profile
            except PartnerProfile.DoesNotExist:
                return Response(
                    {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
                )

            partial = request.method == "PATCH"
            serializer = PartnerProfileSerializer(
                profile, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ----------------------
    @action(detail=True, methods=["post"], url_path="status")
    def change_status(self, request, pk=None):
        partner = self.get_object()
        new_status = request.data.get("status")
        if not new_status:
            return Response(
                {"detail": "Status is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        if new_status not in dict(Partner.PartnerStatus.choices):
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )
        old_status = partner.status
        if old_status == new_status:
            return Response(
                {"detail": "Partner is already in this status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        partner.status = new_status
        partner.save()
        StatusHistory.objects.create(
            partner=partner,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
        )
        return Response({"id": partner.id, "status": partner.status})

    @action(detail=True, methods=["get"], url_path="status-history")
    def status_history(self, request, pk=None):
        """
        GET /api/partners/{id}/status-history/
        Return all status changes for the partner
        """
        partner = self.get_object()
        history = partner.status_history.all().order_by("-changed_at")
        serializer = StatusHistorySerializer(history, many=True)
        return Response(serializer.data)

    # ----------------------
    # --- RISK LEVEL ENDPOINTS ---
    @action(detail=True, methods=["post"], url_path="change_risk")
    def change_risk(self, request, pk=None):
        partner = self.get_object()
        new_level = request.data.get("risk_level")

        # Validate the new risk level
        if new_level not in [choice[0] for choice in Partner.RiskLevel.choices]:
            return Response({"error": "Invalid risk level"}, status=400)

        # Save current risk before updating
        old_level = partner.risk_level
        partner.risk_level = new_level
        partner.save()

        # Log history
        RiskLevelHistory.objects.create(
            partner=partner,
            old_risk=old_level,
            new_risk=new_level,
            changed_by=request.user,
        )

        return Response({"message": "Risk level updated"}, status=200)

    @action(detail=True, methods=["get"])
    def risk_history(self, request, pk=None):
        partner = self.get_object()
        history = partner.risk_history.all()  # Use correct related_name
        serializer = RiskLevelHistorySerializer(history, many=True)
        return Response(serializer.data)


class PartnerDocumentViewSet(viewsets.ModelViewSet):
    """
    Partner Document CRUD:
    - POST → upload document
    - GET → list documents
    - GET /id → retrieve document
    - DELETE → delete document
    """

    queryset = PartnerDocument.objects.all()
    serializer_class = PartnerDocumentSerializer
    permission_classes = [IsSysAdminOrDepartmentUser]

    def get_queryset(self):
        # Correctly return a queryset for the PartnerDocument model.
        partner_id = self.kwargs.get("partner_pk")
        if partner_id:
            # Filters the queryset to only include documents for the specified partner.
            return PartnerDocument.objects.filter(partner_id=partner_id)
        # Fallback for listing all documents if not nested.
        return PartnerDocument.objects.all()

    def perform_create(self, serializer):
        partner_id = self.kwargs.get("partner_pk")
        partner = Partner.objects.get(id=partner_id)
        serializer.save(uploaded_by=self.request.user, partner=partner)
