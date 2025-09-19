from psycopg import IntegrityError
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    MOU,
    Partner,
    PartnerDocument,
    PartnerProfile,
    Project,
    StatusHistory,
    RiskLevelHistory,
    PartnerDepartment,
    ProjectPartner,
)
from users.models import Department

from rest_framework.decorators import action
from .serializers import (
    MOUSerializer,
    PartnerDocumentSerializer,
    PartnerSerializer,
    PartnerDetailSerializer,
    PartnerProfileSerializer,
    StatusHistorySerializer,
    RiskLevelHistorySerializer,
    PartnerDepartmentSerializer,
    PartnerDepartmentDetailSerializer,
    ProjectSerializer,
    PartnershipProjectSerializer,
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

    @action(detail=True, methods=["post"], url_path="departments")
    def assign_departments(self, request, pk=None):
        partner = self.get_object()
        dept_ids = request.data.get("departments", [])
        if not isinstance(dept_ids, list):
            return Response({"error": "departments must be a list"}, status=400)

        assigned = []
        for dept_id in dept_ids:
            try:
                department = Department.objects.get(id=dept_id)
            except Department.DoesNotExist:
                continue  # Skip invalid department

            obj, created = PartnerDepartment.objects.get_or_create(
                partner=partner, department=department
            )
            if created:
                assigned.append(str(department.id))

        return Response(
            {"message": "Departments assigned successfully", "assigned": assigned},
            status=201,
        )

    @action(detail=True, methods=["get"], url_path="list_departments")
    def list_departments(self, request, pk=None):
        partner = self.get_object()
        assignments = partner.partnerdepartment_set.all()
        serializer = PartnerDepartmentDetailSerializer(assignments, many=True)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["delete"], url_path="departments/(?P<dept_id>[^/.]+)")
    def unassign_department(self, request, pk=None, dept_id=None):
        partner = self.get_object()
        try:
            assignment = PartnerDepartment.objects.get(
                partner=partner, department_id=dept_id
            )
            assignment.delete()
            return Response(
                {"message": "Department unassigned successfully"}, status=200
            )
        except PartnerDepartment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=404)


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


# ----------------------
# Project ViewSet


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = "id"
    lookup_value_regex = "[0-9a-f-]{36}"  # UUID regex

    permission_classes = [IsSysAdminOrDepartmentUser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status"]
    search_fields = ["name", "description"]
    ordering_fields = ["start_date", "end_date", "created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["get"], url_path="partners")
    def list_partners(self, request, id=None):
        project = self.get_object()
        # Use the correct related_name from the model
        partnerships = project.project_partners.all()
        serializer = PartnershipProjectSerializer(partnerships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectPartnerViewSet(viewsets.ModelViewSet):
    queryset = ProjectPartner.objects.all()
    serializer_class = PartnershipProjectSerializer
    permission_classes = [IsSysAdminOrDepartmentUser]
    lookup_field = "id"
    lookup_value_regex = "[0-9a-f-]{36}"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["project", "partner", "role", "status"]
    search_fields = ["project__name", "partner__name", "role", "contribution"]
    ordering_fields = ["start_date", "end_date", "created_at", "updated_at"]

    def perform_create(self, serializer):
        try:
            serializer.save()
        except IntegrityError:
            return Response(
                {
                    "detail": "This partner is already assigned to the project with the same role."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="by-partner/(?P<partner_id>[^/.]+)")
    def list_projects_for_partner(self, request, partner_id=None):
        partnerships = self.queryset.filter(partner_id=partner_id)
        serializer = self.get_serializer(partnerships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="by-project/(?P<project_id>[^/.]+)/role/(?P<role>[^/.]+)",
    )
    def list_partners_by_role(self, request, project_id=None, role=None):
        valid_roles = [choice[0] for choice in ProjectPartner.ROLE_CHOICES]
        if role not in valid_roles:
            return Response(
                {"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST
            )

        partnerships = self.queryset.filter(project_id=project_id, role=role)
        serializer = self.get_serializer(partnerships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MOUViewSet(viewsets.ModelViewSet):
    queryset = MOU.objects.all()
    serializer_class = MOUSerializer
    permission_classes = [IsSysAdminOrDepartmentUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "partner__name", "project__name"]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project_id")
        partner_id = self.request.query_params.get("partner_id")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if partner_id:
            qs = qs.filter(partner_id=partner_id)
        return qs
