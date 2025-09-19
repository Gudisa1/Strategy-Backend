from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from .views import (
    MOUViewSet,
    PartnerDocumentViewSet,
    PartnerViewSet,
    ProjectViewSet,
    ProjectPartnerViewSet,
)


router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partners")

router.register(
    r"documents", PartnerDocumentViewSet, basename="documents"
)  # standalone doc access

router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"project-partners", ProjectPartnerViewSet, basename="project-partners")
router.register(r"mous", MOUViewSet, basename="mou")

# Nested router for documents under partner
partners_router = NestedDefaultRouter(router, r"partners", lookup="partner")
partners_router.register(
    r"documents", PartnerDocumentViewSet, basename="partner-documents"
)


urlpatterns = router.urls + partners_router.urls
