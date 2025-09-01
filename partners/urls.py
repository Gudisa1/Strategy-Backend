from rest_framework_nested.routers import NestedDefaultRouter
from rest_framework.routers import DefaultRouter
from .views import PartnerDocumentViewSet, PartnerViewSet


router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partners")

router.register(
    r"documents", PartnerDocumentViewSet, basename="documents"
)  # standalone doc access

# Nested router for documents under partner
partners_router = NestedDefaultRouter(router, r"partners", lookup="partner")
partners_router.register(
    r"documents", PartnerDocumentViewSet, basename="partner-documents"
)


urlpatterns = router.urls + partners_router.urls
