from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Partner, PartnerDocument, PartnerProfile
from rest_framework.decorators import action
from .serializers import (
    PartnerDocumentSerializer,
    PartnerSerializer,
    PartnerDetailSerializer,
    PartnerProfileSerializer,
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
