from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name="currency-home"),
    path('latest', views.get_latest_rate, name="currency-latest"),
    re_path(r'^(?P<start_date_string>\d{4}-\d{2}-\d{2})\.\.(?P<end_date_string>\d{4}-\d{2}-\d{2})/$', views.get_interval_rate, name='currency-interval'),
]