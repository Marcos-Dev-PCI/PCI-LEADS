from django.urls import path
from .views import LeadListCreateView, LeadDetailView, LeadSearchView, UserMeView 

from rest_framework.authtoken.views import obtain_auth_token # Linha adicionada

urlpatterns = [
    path("", LeadListCreateView.as_view(), name="lead-list-create"),
    path("<int:pk>/", LeadDetailView.as_view(), name="lead-detail"),
    path("search/", LeadSearchView.as_view(), name="lead-search"),

    # 1. Endpoint de Login exigido pela demanda:
    path('api/auth/login/', obtain_auth_token, name='api_token_auth'),

    # 2. Endpoint de Usuário Atual exigido pela demanda:
    path('api/auth/me/', UserMeView.as_view(), name='api_user_me'),
]
