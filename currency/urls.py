from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="currency-home"),
    path('latest', views.get_latest_rate, name="currency-latest"),
    path('interval/', views.get_interval_rate, name="currency-interval"),
]