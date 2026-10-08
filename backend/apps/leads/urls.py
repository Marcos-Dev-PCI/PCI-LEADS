from django.urls import path
from .views import LeadListCreateView, LeadDetailView, LeadSearchView

urlpatterns = [
    path("", LeadListCreateView.as_view(), name="lead-list-create"),
    path("<int:pk>/", LeadDetailView.as_view(), name="lead-detail"),
    path("search/", LeadSearchView.as_view(), name="lead-search"),
]
