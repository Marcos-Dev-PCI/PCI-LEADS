from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/leads/", include("apps.leads.urls")),
    
    # Rota de login do DRF que gera e devolve o Token
    path("api/auth/login/", obtain_auth_token, name="api_login"),
]