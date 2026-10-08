from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from apps.leads.views import UserMeView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Autenticação
    path("api/auth/login/", obtain_auth_token, name="api-login"),
    path("api/auth/me/", UserMeView.as_view(), name="api-me"),
    # Leads
    path("api/leads/", include("apps.leads.urls")),
]