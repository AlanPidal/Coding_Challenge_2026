from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # /dashboard/ -> portfolio.views.dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("wallet/<int:pk>/delete/", views.delete_wallet, name="delete_wallet"),
]
