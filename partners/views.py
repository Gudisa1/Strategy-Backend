from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Partner, PartnerProfile
from rest_framework.views import APIView
from .serializers import (
    PartnerSerializer,
    PartnerDetailSerializer,
    PartnerProfileSerializer,
)
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
