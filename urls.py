from django.contrib import admin
from django.urls import path, include
from portfolio import views as portfolio_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Incluimos las URLs de la app portfolio en la raíz
    path("", include("portfolio.urls", namespace="portfolio")),  # /dashboard/
    # Redirige la raíz "/" a "/dashboard/"
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
     Rutas de autenticación: login y logout usando templates en registration/
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),
    # Ruta para registro (vista definida en portfolio.views)
    path("accounts/register/", portfolio_views.register_view, name="register"),
]
